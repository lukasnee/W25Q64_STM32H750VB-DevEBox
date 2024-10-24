"""
TODO: Add a description of the script
"""

import sys
import os

from struct import unpack
from time import sleep, time
import argparse

from min import MINTransportSerial
import logging
from enum import Enum
from ctypes import Structure, c_uint8

import comm_pb2 as pb

parser = argparse.ArgumentParser(description='MIN Transport Serial')
parser.add_argument('file', type=str, help='File to flash')
parser.add_argument('-D', '--port', type=str,
                    default='/dev/ttyACM0', help='MIN port')
parser.add_argument('-b,', '--baudrate', type=int,
                    default=921600, help='MIN baudrate')
args = parser.parse_args()


def wait_for_responses(min_handler: MINTransportSerial, timeout: float = 15.0):
    start_time = time()
    while True:
        # The polling will generally block waiting for characters on a timeout
        # How much CPU time this takes depends on the Python serial implementation
        # on the target machine
        frames = min_handler.poll()
        if frames:
            return frames
        if time() - start_time > timeout:
            return None


def wait_for_response(min_handler: MINTransportSerial, min_id: int, timeout: float = 15.0):
    while True:
        frames = wait_for_responses(min_handler, timeout)
        if not frames:
            print("Timeout waiting for frame")
            return None
        for frame in frames:
            if frame.min_id != min_id:
                print(f"Unexpected min_id: {pb.COMM_CMD.Name(frame.min_id)}")
                continue
            return frame


def queue_request(min_handler: MINTransportSerial, min_id: int, rq: Structure):
    # print(f"queue_request(min_id={pb.COMM_CMD.Name(min_id)}):")
    min_handler.queue_frame(min_id=min_id, payload=rq.SerializeToString())


def comm_cmd_sector_erase(min_handler: MINTransportSerial, addr_start: int, addr_end: int):
    print(
        f"comm_cmd_sector_erase(addr_start=0x{addr_start:08X}, addr_end=0x{addr_end:08X}): ", end="")
    comm_cmd_qspi_sector_erase = pb.CommCmdQspiSectorEraseRq()
    comm_cmd_qspi_sector_erase.addr_start = addr_start
    comm_cmd_qspi_sector_erase.addr_end = addr_end
    queue_request(min_handler, pb.COMM_CMD.QSPI_SECTOR_ERASE,
                  comm_cmd_qspi_sector_erase)
    frame = wait_for_response(
        min_handler, pb.COMM_CMD.QSPI_SECTOR_ERASE, 10)
    if not frame:
        return False
    rp = pb.CommCmdBasicRp()
    rp.ParseFromString(frame.payload)
    if rp.result != pb.COMM_RES.OK:
        sleep(0.1)
        print(f"{pb.COMM_RES.Name(rp.result)}")
        return False
    print(f"{pb.COMM_RES.Name(rp.result)}")
    return True


def comm_cmd_write_file_using_flash_commands(min_handler: MINTransportSerial, file_path: str, offset: int):
    print(
        f"comm_cmd_write_file_using_flash_commands(file_path={file_path}, offset=0x{offset:08X}):")
    MAX_BUFF_SIZE = 128
    comm_cmd_qspi_write = pb.CommCmdQspiWriteRq()
    file_size = os.path.getsize(file_path)
    comm_cmd_sector_erase(min_handler, offset, offset + file_size)
    print(f"Flashing file of size: {file_size}")
    with open(file_path, 'rb') as file:
        comm_cmd_qspi_write.addr = offset
        write_buff = file.read(MAX_BUFF_SIZE)
        comm_cmd_qspi_write.buff = write_buff
        while len(write_buff) > 0:
            print(
                f"Flashing {len(write_buff)} bytes at addr {comm_cmd_qspi_write.addr}/{file_size} ({(comm_cmd_qspi_write.addr/file_size)*100:.2f} %)", end="\r")
            queue_request(min_handler, pb.COMM_CMD.QSPI_WRITE,
                          comm_cmd_qspi_write)
            frame = wait_for_response(min_handler, pb.COMM_CMD.QSPI_WRITE)
            if not frame:
                return False
            rp = pb.CommCmdBasicRp()
            rp.ParseFromString(frame.payload)
            if rp.result != pb.COMM_RES.OK:
                print(f"Error flashing: {pb.COMM_RES.Name(rp.result)}")
                continue
            comm_cmd_qspi_write.addr += len(write_buff)
            write_buff = file.read(MAX_BUFF_SIZE)
            comm_cmd_qspi_write.buff = write_buff
        print("")

        print("Verifying flash: ", end="")
        file.seek(0)
        comm_cmd_qspi_read = pb.CommCmdQspiReadRq()
        comm_cmd_qspi_read.addr = offset
        comm_cmd_qspi_read.len = min(file_size, MAX_BUFF_SIZE)
        while comm_cmd_qspi_read.addr < offset + file_size:
            print(
                f"Verifying {comm_cmd_qspi_read.addr}/{offset + file_size} ({(comm_cmd_qspi_read.addr/(offset + file_size))*100:.2f} %)", end="\r")
            queue_request(min_handler, pb.COMM_CMD.QSPI_READ,
                          comm_cmd_qspi_read)
            frame = wait_for_response(min_handler, pb.COMM_CMD.QSPI_READ)
            if not frame:
                return False
            rp = pb.CommCmdQspiReadRp()
            rp.ParseFromString(frame.payload)
            if rp.buff != file.read(len(rp.buff)):
                print("Verification failed at addr: 0x{:08X}".format(
                    comm_cmd_qspi_read.addr))
                return False
            comm_cmd_qspi_read.addr += len(rp.buff)
            comm_cmd_qspi_read.len = min(
                file_size - comm_cmd_qspi_read.addr, MAX_BUFF_SIZE)
        print("")
    return True


def comm_cmd_qspi_mass_erase(min_handler: MINTransportSerial):
    print("comm_cmd_qspi_mass_erase: ", end="")
    queue_request(min_handler, pb.COMM_CMD.QSPI_MASS_ERASE,
                  pb.CommCmdQspiMassEraseRq())
    frame = wait_for_response(min_handler, pb.COMM_CMD.QSPI_MASS_ERASE)
    if not frame:
        return False
    rp = pb.CommCmdBasicRp()
    rp.ParseFromString(frame.payload)
    if rp.result != pb.COMM_RES.OK:
        print(f"{pb.COMM_RES.Name(rp.result)}")
        return False
    print(f"{pb.COMM_RES.Name(rp.result)}")
    return True


def comm_cmd_bootloader_intercept(min_handler: MINTransportSerial, state: bool):
    intercept_rq = pb.CommCmdBootloaderInterceptRq(intercept=state)
    print(f"comm_cmd_bootloader_intercept(state={state}): ", end="")
    queue_request(min_handler, pb.COMM_CMD.BOOTLOADER_INTERCEPT, intercept_rq)
    frame = wait_for_response(min_handler, pb.COMM_CMD.BOOTLOADER_INTERCEPT)
    if not frame:
        return False
    rp = pb.CommCmdBasicRp()
    rp.ParseFromString(frame.payload)
    if rp.result != pb.COMM_RES.OK:
        print(f"{pb.COMM_RES.Name(rp.result)}")
        return False
    print(f"{pb.COMM_RES.Name(rp.result)}")
    return True


if __name__ == "__main__":
    min_handler = MINTransportSerial(
        port=args.port, baudrate=args.baudrate, loglevel=1)

    min_handler.transport_reset()

    comm_cmd_bootloader_intercept(min_handler, True)
    comm_cmd_write_file_using_flash_commands(min_handler, args.file, 0)
    comm_cmd_bootloader_intercept(min_handler, False)
