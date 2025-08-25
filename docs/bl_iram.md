# `bl_iram`

Bootloader that loads application firmware from the external QSPI flash memory
(W25Q64) to the internal D1 domain 512 KiB AXI-SRAM and executes it from there.
The application firmware is stored as a file in a littlefs file system that is
mounted on the external non-volatile flash memory. On reset, the bootloader runs
the `comm` service and briefly waits for client interception for uploading a new
firmware via UART from a host computer. If no client interaction is detected
within a second, the bootloader loads the application firmware into volatile RAM
and jumps to it.

The bootloader itself is stored in the internal flash memory.

## Building Application Firmware

To build a compatible application firmware for `bl_iram` firmware, link it with
[`bl_iram_app.ld`](../linker/bl_iram_app.ld) linker script. This is a basic
linker file that maps the application firmware to the internal D1 domain 512 KiB
AXI-SRAM memory region and hides the region where the bootloader is stored.
