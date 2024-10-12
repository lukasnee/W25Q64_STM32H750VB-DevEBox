# `bl_iram`

Bootloader that loads a program from the QSPI flash to the internal D1 domain
512 KiB AXI-SRAM and executes it. Bootloader on startup runs the `comm` service
that allows you to upload a new firmware via UART from a host computer.

The bootloader itself is stored in the internal flash memory.

## Building

```bash
git submodule update --recursive --init
make VARIANT=bl_iram
```

Further instructions on flashing, and debugging can be found in the [common
instructions](bl_common.md).
