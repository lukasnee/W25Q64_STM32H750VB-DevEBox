# `bl_iram`

Bootloader that loads a program from the QSPI flash to the internal D1 domain
512 KiB AXI-SRAM and executes it. Bootloader on startup runs the `comm` service
that allows you to upload a new firmware via UART from a host computer.

The bootloader itself is stored in the internal flash memory.

## Building Bootloader Firmware

> **Note:** prerequisites in the [common instructions](bl_common.md) are required!

```bash
git submodule update --recursive --init
make VARIANT=bl_iram
```

Further instructions on flashing, and debugging can be found in the [common
instructions](bl_common.md).

## Building Application Firmware

To build a compatible application firmware for `bl_iram` firmware, link it with
[`bl_iram_app.ld`](../linker/bl_iram_app.ld) linker script. This is a basic
linker file that maps the application firmware to the internal D1 domain 512 KiB
AXI-SRAM memory region and hides the region where the bootloader is stored.
