
#include "comm/comm.h"

#include "pb_encode.h"
#include "pb_decode.h"
#include "comm.pb.h"

#include "stm32h7xx_hal.h"

#include "min.h"

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

void queue_basic_response(uint8_t min_id, COMM_RES res)
{
    CommCmdBasicRp rp = CommCmdBasicRp_init_default;
    rp.result = res;
    uint8_t buffer[CommCmdBasicRp_size];
    pb_ostream_t stream = pb_ostream_from_buffer(buffer, sizeof(buffer));
    pb_encode(&stream, CommCmdBasicRp_fields, &rp);
    min_queue_frame(&min_ctx, min_id, buffer, stream.bytes_written);
}

void comm_handle(uint8_t min_id, const CommCmdQspiWriteRq &rq)
{
    __set_PRIMASK(0);
    if (HAL_OK != HAL_QSPI_Abort(&hqspi)) {
        __set_PRIMASK(1);
        return queue_basic_response(min_id, COMM_RES_ERR_QSPI_ABORT);
    }
    if (HAL_OK != CSP_QSPI_WriteMemory(const_cast<uint8_t *>(rq.buff.bytes),
                                       rq.addr, rq.buff.size)) {
        __set_PRIMASK(1);
        return queue_basic_response(min_id, COMM_RES_ERR_QSPI_WRITE);
    }
    __set_PRIMASK(1);
    return queue_basic_response(min_id, COMM_RES_OK);
}

void comm_handle(uint8_t min_id, const CommCmdQspiMassEraseRq &rq)
{
    __set_PRIMASK(0);
    if (HAL_OK != HAL_QSPI_Abort(&hqspi)) {
        __set_PRIMASK(1);
        return queue_basic_response(min_id, COMM_RES_ERR_QSPI_ABORT);
    }
    if (HAL_OK != CSP_QSPI_Erase_Chip()) {
        __set_PRIMASK(1);
        return queue_basic_response(min_id, COMM_RES_ERR_QSPI_ERASE);
    }
    __set_PRIMASK(1);
    return queue_basic_response(min_id, COMM_RES_OK);
}

template <typename T>
void comm_handle(const pb_msgdesc_t *fields, uint8_t min_id,
                 const uint8_t *data, uint8_t size)
{
    T rq;
    pb_istream_t stream = pb_istream_from_buffer(data, size);
    if (!pb_decode(&stream, fields, &rq)) {
        return queue_basic_response(min_id, COMM_RES_ERR_PARSE_RQ);
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
    HANDLE(COMM_CMD_BOOTLOADER_INTERCEPT, CommCmdBootloaderInterceptRq);       \
    HANDLE(COMM_CMD_QSPI_MASS_ERASE, CommCmdQspiMassEraseRq);

        HANDLES;

#undef HANDLES
#undef HANDLE
    default:
        return queue_basic_response(min_id, COMM_RES_ERR_UNKNOWN_CMD);
    }
}

static bool intercepted = false;

void comm_handle(uint8_t min_id, const CommCmdBootloaderInterceptRq &rq)
{
    intercepted = rq.intercept != 0;
    queue_basic_response(min_id, COMM_RES_OK);
}

extern "C" void comm_init()
{
    min_init_context(&min_ctx, 0);
    min_transport_reset(&min_ctx, true);
    const uint32_t initial_uptime = HAL_GetTick();
    const uint32_t comm_intercept_time_window = 3000;
    while (intercepted ||
           HAL_GetTick() - initial_uptime < comm_intercept_time_window) {
        uint8_t byte;
        if (HAL_UART_Receive(&huart4, &byte, sizeof(byte), 1) != HAL_OK) {
            min_poll(&min_ctx, nullptr, 0);
            continue;
        }
        min_poll(&min_ctx, &byte, 1);
    }
}
