# `bl_qspiflash`

Bootloader that Executes In Place (XIP) program stored on QSPI flash memory.
Bootloader on startup runs the `comm` service that allows you to upload a new
firmware via UART from a host computer.

The bootloader itself is stored in the internal flash memory.

## Building Application Firmware

To build a compatible application firmware for `bl_qspiflash` firmware, link it
with [`bl_qspiflash_app.ld`](../linker/bl_qspiflash_app.ld) linker script. This
is a basic linker file that maps the application firmware to the QSPI flash
memory memory region and hides the region where the bootloader is stored.
