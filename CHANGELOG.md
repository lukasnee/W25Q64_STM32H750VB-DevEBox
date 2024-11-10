## 0.2.0 (2024-11-11)

### Feat

- comm_cmd_lfs_write and successful file flashing
- comm_cmd_lfs_open and comm_cmd_lfs_close
- simple littlefs protobuf for reading and writing files
- QSPI FLASH littlefs integration

### Fix

- minor compilation warning

### Refactor

- **comm.py**: resolve TODOs
- **comm.py**: extract transact method
- **comm.py**: encapsulate into class Comm
- **comm.py**: embrace except error handling
- **comm.py**: improve bootloader interception
- **comm.py**: logging
- **comm.py**: parse_args
- **comm.py**: improve bootloader interception
- **comm.py**: improve bootloader interception
- comm.py
- W25Q QSPI FLASH API and add doxygen
- comm_init -> comm_service
- **makefile**: fix trailing whitespaces

## 0.1.0 (2024-10-13)

### Feat

- COMM_CMD_QSPI_READ
- COMM_QSPI_SECTOR_ERASE
- comm client/server
- add comm.proto
- UART4 in blocking mode
- debugging capabilities
- VARIANT=ext_loader

### Fix

- unable to write/erase FLASH after entering memory mapped mode

### Refactor

- comm_queue_response
- crc validation
- jump_to_app
