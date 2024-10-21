
#include "comm/comm.h"

#include "pb_encode.h"
#include "pb_decode.h"
#include "comm.pb.h"

#include "stm32h7xx_hal.h"

#include "min.h"
#include "lfsapp/lfsapp.h"

#include "quadspi.h"

#include <stdbool.h>
#include <stdint.h>

extern UART_HandleTypeDef huart4;

struct min_context min_ctx;

// MIN API START

extern "C" void min_tx_start(uint8_t port)
{
}

extern "C" void min_tx_finished(uint8_t port)
{
}

extern "C" uint16_t min_tx_space(uint8_t port)
{
    if (port == 0) {
        return 512U; // This is a lie but we will handle the consequences
    }
    else {
        return 0;
    }
}

// Send a character on the designated port.
extern "C" void min_tx_byte(uint8_t port, uint8_t byte)
{
    if (port == 0) {
        HAL_UART_Transmit(&huart4, &byte, 1, 1);
    }
    else {
    }
}

extern "C" uint32_t min_time_ms(void)
{
    return HAL_GetTick();
}

// MIN API END

static void _comm_queue_response(uint8_t min_id, const void *payload,
                                 const pb_msgdesc_t *fields)
{
    uint8_t buffer[MAX_PAYLOAD];
    pb_ostream_t stream = pb_ostream_from_buffer(buffer, sizeof(buffer));
    pb_encode(&stream, fields, payload);
    min_queue_frame(&min_ctx, min_id, buffer, stream.bytes_written);
}

#define comm_queue_response(type, id, payload)                                 \
    _comm_queue_response(id, payload, type##_fields)

void comm_queue_response_basic(uint8_t min_id, COMM_RES res)
{
    CommCmdBasicRp rp = CommCmdBasicRp_init_default;
    rp.result = res;
    comm_queue_response(CommCmdBasicRp, min_id, &rp);
}

void comm_handle(uint8_t min_id, const CommCmdQspiReadRq &rq)
{
    CommCmdQspiReadRp rp = CommCmdQspiReadRp_init_default;
    if (rq.len > sizeof(rp.buff.bytes)) {
        return comm_queue_response_basic(min_id,
                                         COMM_RES_ERR_QSPI_OUT_OF_RANGE);
    }
    if ((rq.addr + rq.len) > (1 << (hqspi.Init.FlashSize + 1))) {
        return comm_queue_response_basic(min_id,
                                         COMM_RES_ERR_QSPI_OUT_OF_RANGE);
    }
    rp.addr = rq.addr;
    rp.buff.size = rq.len;
    W25Q_EnableMemoryMappedMode2();
    memcpy(rp.buff.bytes, reinterpret_cast<const void *>(QSPI_BASE + rq.addr),
           rq.len);
    comm_queue_response(CommCmdQspiReadRp, min_id, &rp);
}

void comm_handle(uint8_t min_id, const CommCmdQspiWriteRq &rq)
{
    __set_PRIMASK(0);
    if (HAL_OK != W25Q_WriteMemory(const_cast<uint8_t *>(rq.buff.bytes),
                                   rq.addr, rq.buff.size)) {
        __set_PRIMASK(1);
        return comm_queue_response_basic(min_id, COMM_RES_ERR_QSPI_WRITE);
    }
    __set_PRIMASK(1);
    return comm_queue_response_basic(min_id, COMM_RES_OK);
}

void comm_handle(uint8_t min_id, const CommCmdQspiSectorEraseRq &rq)
{
    if (HAL_OK != W25Q_EraseSector(rq.addr_start, rq.addr_end)) {
        return comm_queue_response_basic(min_id,
                                         COMM_RES_ERR_QSPI_SECTOR_ERASE);
    }
    return comm_queue_response_basic(min_id, COMM_RES_OK);
}

void comm_handle(uint8_t min_id, const CommCmdQspiMassEraseRq &rq)
{
    __set_PRIMASK(0);
    if (HAL_OK != W25Q_Erase_Chip()) {
        __set_PRIMASK(1);
        return comm_queue_response_basic(min_id, COMM_RES_ERR_QSPI_MASS_ERASE);
    }
    __set_PRIMASK(1);
    return comm_queue_response_basic(min_id, COMM_RES_OK);
}

static lfs_file_t lfs_file;

void comm_handle(uint8_t min_id, const CommLfsOpenRq &rq)
{
    CommLfsOpenRp rp = CommLfsOpenRp_init_default;
    rp.result = lfs_file_open(&lfs, &lfs_file, rq.path, rq.flags);
    comm_queue_response(CommLfsOpenRp, min_id, &rp);
}

void comm_handle(uint8_t min_id, const CommLfsCloseRq &rq)
{
    CommLfsCloseRp rp = CommLfsCloseRp_init_default;
    rp.result = lfs_file_close(&lfs, &lfs_file);
    comm_queue_response(CommLfsCloseRp, min_id, &rp);
}

void comm_handle(uint8_t min_id, const CommLfsReadRq &rq)
{
    CommLfsReadRp rp = CommLfsReadRp_init_default;
    rp.result = lfs_file_read(&lfs, &lfs_file, rp.buff.bytes, rq.len);
    rp.buff.size = rq.len;
    comm_queue_response(CommLfsReadRp, min_id, &rp);
}

void comm_handle(uint8_t min_id, const CommLfsWriteRq &rq)
{
    CommLfsWriteRp rp = CommLfsWriteRp_init_default;
    rp.result = lfs_file_write(&lfs, &lfs_file, rq.buff.bytes, rq.buff.size);
    comm_queue_response(CommLfsWriteRp, min_id, &rp);
}

template <typename T>
void comm_handle(const pb_msgdesc_t *fields, uint8_t min_id,
                 const uint8_t *data, uint8_t size)
{
    T rq;
    pb_istream_t stream = pb_istream_from_buffer(data, size);
    if (!pb_decode(&stream, fields, &rq)) {
        return comm_queue_response_basic(min_id, COMM_RES_ERR_PARSE_RQ);
    }
    comm_handle(min_id, rq);
}

extern "C" void min_application_handler(uint8_t min_id, uint8_t const *data,
                                        uint8_t size, uint8_t port)
{
    switch (min_id) {
#define HANDLE(cmd, type)                                                      \
    case cmd:                                                                  \
        return comm_handle<type>(type##_fields, min_id, data, size)
#define HANDLES                                                                \
    HANDLE(COMM_CMD_QSPI_WRITE, CommCmdQspiWriteRq);                           \
    HANDLE(COMM_CMD_QSPI_READ, CommCmdQspiReadRq);                             \
    HANDLE(COMM_CMD_QSPI_SECTOR_ERASE, CommCmdQspiSectorEraseRq);              \
    HANDLE(COMM_CMD_BOOTLOADER_INTERCEPT, CommCmdBootloaderInterceptRq);       \
    HANDLE(COMM_CMD_QSPI_MASS_ERASE, CommCmdQspiMassEraseRq);                  \
    HANDLE(COMM_CMD_LFS_OPEN, CommLfsOpenRq);                                  \
    HANDLE(COMM_CMD_LFS_CLOSE, CommLfsCloseRq);                                \
    HANDLE(COMM_CMD_LFS_READ, CommLfsReadRq);                                  \
    HANDLE(COMM_CMD_LFS_WRITE, CommLfsWriteRq);

        HANDLES;

#undef HANDLES
#undef HANDLE
    default:
        return comm_queue_response_basic(min_id, COMM_RES_ERR_UNKNOWN_CMD);
    }
}

static bool intercepted = false;

void comm_handle(uint8_t min_id, const CommCmdBootloaderInterceptRq &rq)
{
    intercepted = rq.intercept != 0;
    comm_queue_response_basic(min_id, COMM_RES_OK);
}

extern "C" void comm_service(uint32_t listen_time_ms)
{
    min_init_context(&min_ctx, 0);
    min_transport_reset(&min_ctx, true);
    const uint32_t initial_uptime_ms = min_time_ms();
    while (intercepted || min_time_ms() - initial_uptime_ms < listen_time_ms) {
        uint8_t byte;
        if (HAL_UART_Receive(&huart4, &byte, sizeof(byte), 1) != HAL_OK) {
            min_poll(&min_ctx, nullptr, 0);
            continue;
        }
        min_poll(&min_ctx, &byte, 1);
    }
}
