"""
TODO: Add a description of the script
"""

import sys
import os

from time import time
import argparse

from min import MINTransportSerial
import logging

import comm_pb2 as pb
import humanize


log = logging.getLogger("comm")


def fn_name():
    return sys._getframe(1).f_code.co_name


class Comm:
    # TODO: decouple args
    def __init__(self, args):
        self.min_handler = MINTransportSerial(
            port=args.port, baudrate=args.baudrate, loglevel=logging.WARNING)
        self.min_handler.transport_reset()

    # General Commands

    def await_bootloader(self,
                         timeout: float = 10.0):
        log.debug(f"{fn_name()}()")
        print("Please reset the device. Waiting", end="")
        sys.stdout.flush()
        start_time = time()
        while True:
            try:
                intercept_rq = pb.CommCmdInterceptRq()
                self.send_request(pb.COMM_CMD.INTERCEPT, intercept_rq)
                frame = self.await_response(pb.COMM_CMD.INTERCEPT, 1.0)
                rp = pb.CommCmdBasicRp()
                rp.ParseFromString(frame.payload)
                if rp.result != pb.COMM_RES.OK:
                    log.error(f"{fn_name()}(): {pb.COMM_RES.Name(rp.result)}")
                    raise Exception(f"{pb.COMM_RES.Name(rp.result)}")
                log.debug(f"{fn_name()}(): {pb.COMM_RES.Name(rp.result)}")
                break
            except TimeoutError:
                print(".", end="")
                sys.stdout.flush()
            if time() - start_time > timeout:
                raise TimeoutError()

    def release_bootloader(self, timeout: float = 1.0):
        log.debug(f"{fn_name()}()")
        comm_cmd_release_rq = pb.CommCmdReleaseRq()
        self.send_request(pb.COMM_CMD.RELEASE,
                          comm_cmd_release_rq)
        frame = self.await_response(pb.COMM_CMD.RELEASE, timeout)
        rp = pb.CommCmdBasicRp()
        rp.ParseFromString(frame.payload)
        if rp.result != pb.COMM_RES.OK:
            raise Exception(f"{pb.COMM_RES.Name(rp.result)}")
        log.debug(f"{fn_name()}(): {pb.COMM_RES.Name(rp.result)}")

    def flash_app(self, file_path: str):
        self.transfer_file(file_path, "boot/app.bin")

    # LittleFS (File System) Commands

    def cmd_lfs_open(self, file_path: str, flags: int):
        log.debug(f"{fn_name()}(file_path={file_path})")
        comm_cmd_fopen_rq = pb.CommCmdLfsOpenRq()
        comm_cmd_fopen_rq.path = file_path
        comm_cmd_fopen_rq.flags = flags
        self.send_request(pb.COMM_CMD.LFS_OPEN,
                          comm_cmd_fopen_rq)
        frame = self.await_response(pb.COMM_CMD.LFS_OPEN)
        rp = pb.CommCmdLfsOpenRp()
        rp.ParseFromString(frame.payload)
        if rp.result != pb.COMM_LFS_ERR.LFS_ERR_OK:
            raise Exception(f"{pb.COMM_LFS_ERR.Name(rp.result)}")
        log.debug(f"{fn_name()}(): {pb.COMM_LFS_ERR.Name(rp.result)}")

    def cmd_lfs_close(self):
        log.debug(f"{fn_name()}()")
        comm_cmd_fclose_rq = pb.CommCmdLfsCloseRq()
        self.send_request(pb.COMM_CMD.LFS_CLOSE,
                          comm_cmd_fclose_rq)
        frame = self.await_response(pb.COMM_CMD.LFS_CLOSE)
        rp = pb.CommCmdBasicRp()
        rp.ParseFromString(frame.payload)
        if rp.result != pb.COMM_LFS_ERR.LFS_ERR_OK:
            raise Exception(f"{pb.COMM_LFS_ERR.Name(rp.result)}")
        log.debug(f"{fn_name()}(): {pb.COMM_LFS_ERR.Name(rp.result)}")

    def cmd_lfs_write(self, buff: bytes):
        log.debug(f"{fn_name()}()")
        comm_cmd_fwrite_rq = pb.CommCmdLfsWriteRq()
        if len(buff) > 128:
            raise Exception(f"buff size too large: {len(buff)} > 128")
        comm_cmd_fwrite_rq.buff = buff
        self.send_request(pb.COMM_CMD.LFS_WRITE,
                          comm_cmd_fwrite_rq)
        frame = self.await_response(pb.COMM_CMD.LFS_WRITE)
        rp = pb.CommCmdLfsWriteRp()
        rp.ParseFromString(frame.payload)
        if rp.result < pb.COMM_LFS_ERR.LFS_ERR_OK:
            raise Exception(f"{pb.COMM_LFS_ERR.Name(rp.result)}")
        log.debug(
            f"{fn_name()}(): {pb.COMM_LFS_ERR.Name(rp.result) if rp.result == 0 else rp.result}")

    def transfer_file(self, local_src_path: str, remote_dst_path: str):
        self.cmd_lfs_open(remote_dst_path, pb.COMM_LFS_O.LFS_O_RDWR |
                          pb.COMM_LFS_O.LFS_O_CREAT | pb.COMM_LFS_O.LFS_O_TRUNC)
        bytes_written = 0
        last_time = time()
        last_bytes_written = 0
        bytes_per_second_humanized = 0
        with open(local_src_path, 'rb') as file:
            buff = file.read(128)
            print(" " * 100, end="\r")
            while len(buff) > 0:
                print(
                    f"Transferring '{local_src_path}' to '{remote_dst_path}' {(file.tell()/os.path.getsize(local_src_path))*100:.2f}% @ {bytes_per_second_humanized}/s", end="\r")
                self.cmd_lfs_write(buff)
                buff = file.read(128)
                bytes_written += len(buff)

                if time() - last_time > 1.0:
                    bytes_per_second_humanized = humanize.naturalsize(
                        bytes_written - last_bytes_written)
                    last_bytes_written = bytes_written
                    last_time = time()
            print("")
        self.cmd_lfs_close()

    # QSPI FLASH Commands

    def cmd_sector_erase(self, addr_start: int, addr_end: int):
        log.debug(
            f"{fn_name()}(addr_start=0x{addr_start:08X}, addr_end=0x{addr_end:08X})")
        comm_cmd_qspi_sector_erase = pb.CommCmdQspiSectorEraseRq()
        comm_cmd_qspi_sector_erase.addr_start = addr_start
        comm_cmd_qspi_sector_erase.addr_end = addr_end
        self.send_request(pb.COMM_CMD.QSPI_SECTOR_ERASE,
                          comm_cmd_qspi_sector_erase)
        frame = self.await_response(pb.COMM_CMD.QSPI_SECTOR_ERASE, 10)
        rp = pb.CommCmdBasicRp()
        rp.ParseFromString(frame.payload)
        if rp.result != pb.COMM_RES.OK:
            raise Exception(f"{pb.COMM_RES.Name(rp.result)}")
        log.debug(f"{pb.COMM_RES.Name(rp.result)}")

    def cmd_qspi_mass_erase(self):
        log.debug(f"{fn_name()}()")
        self.send_request(pb.COMM_CMD.QSPI_MASS_ERASE,
                          pb.CommCmdQspiMassEraseRq())
        frame = self.await_response(pb.COMM_CMD.QSPI_MASS_ERASE)
        rp = pb.CommCmdBasicRp()
        rp.ParseFromString(frame.payload)
        if rp.result != pb.COMM_RES.OK:
            raise Exception(f"{pb.COMM_RES.Name(rp.result)}")
        log.debug(f"{fn_name()}(): {pb.COMM_RES.Name(rp.result)}")

    def transfer_file_using_flash_commands(self, file_path: str, offset: int):
        log.debug(
            f"{fn_name()}(file_path={file_path}, offset=0x{offset:08X}):")
        MAX_BUFF_SIZE = 128
        comm_cmd_qspi_write = pb.CommCmdQspiWriteRq()
        file_size = os.path.getsize(file_path)
        self.cmd_sector_erase(offset, offset + file_size)
        print(f"Flashing file of size: {file_size}")
        with open(file_path, 'rb') as file:
            comm_cmd_qspi_write.addr = offset
            write_buff = file.read(MAX_BUFF_SIZE)
            comm_cmd_qspi_write.buff = write_buff
            while len(write_buff) > 0:
                print(
                    f"Flashing {len(write_buff)} bytes at addr {comm_cmd_qspi_write.addr}/{file_size} ({(comm_cmd_qspi_write.addr/file_size)*100:.2f} %)", end="\r")
                self.send_request(pb.COMM_CMD.QSPI_WRITE,
                                  comm_cmd_qspi_write)
                frame = self.await_response(pb.COMM_CMD.QSPI_WRITE)
                rp = pb.CommCmdBasicRp()
                rp.ParseFromString(frame.payload)
                if rp.result != pb.COMM_RES.OK:
                    log.error(f"Error flashing: {pb.COMM_RES.Name(rp.result)}")
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
                self.send_request(pb.COMM_CMD.QSPI_READ,
                                  comm_cmd_qspi_read)
                frame = self.await_response(pb.COMM_CMD.QSPI_READ)
                rp = pb.CommCmdQspiReadRp()
                rp.ParseFromString(frame.payload)
                if rp.buff != file.read(len(rp.buff)):
                    raise Exception(
                        f"Verification failed at addr: 0x{comm_cmd_qspi_read.addr:08X}")
                comm_cmd_qspi_read.addr += len(rp.buff)
                comm_cmd_qspi_read.len = min(
                    file_size - comm_cmd_qspi_read.addr, MAX_BUFF_SIZE)
            print("")

    def await_response(self, min_id: int, timeout: float = 15.0):
        start_time = time()
        while True:
            # The polling will generally block waiting for characters on a timeout
            # How much CPU time this takes depends on the Python serial implementation
            # on the target machine
            frames = self.min_handler.poll()
            for frame in frames:
                if frame.min_id != min_id:
                    log.error(
                        f"Unexpected min_id: {pb.COMM_CMD.Name(frame.min_id)}")
                    continue
                return frame
            if time() - start_time > timeout:
                raise TimeoutError()

    def send_request(self, min_id: int, rq):
        log.debug(f"{fn_name()}(min_id={pb.COMM_CMD.Name(min_id)}, rq={rq})")
        self.min_handler.queue_frame(
            min_id=min_id, payload=rq.SerializeToString())


def parse_args():
    parser = argparse.ArgumentParser(description='MIN Transport Serial')
    # TODO clarify this argument, specify that it's app.bin
    parser.add_argument('file', type=str, help='File to flash')
    parser.add_argument('-D', '--port', type=str,
                        default='/dev/ttyACM0', help='MIN port')
    parser.add_argument('-b,', '--baudrate', type=int,
                        default=921600, help='MIN baudrate')
    parser.add_argument('-l', '--loglevel', type=int,
                        default=logging.WARNING, help='Log level (DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50)')
    parser.add_argument('-L', '--logfile', type=str,
                        default='comm.log', help='Log file')
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(filename=args.logfile,
                        level=args.loglevel,
                        format='%(asctime)s|%(levelname)s|%(name)s|%(message)s')
    comm = Comm(args)
    comm.await_bootloader(10.0)
    comm.flash_app(args.file)
    comm.release_bootloader()


if __name__ == "__main__":
    main()
