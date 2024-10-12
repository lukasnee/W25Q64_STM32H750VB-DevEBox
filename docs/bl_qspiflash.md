# `bl_qspiflash`

Bootloader that Executes In Place (XIP) program stored on QSPI flash memory.
Bootloader on startup runs the `comm` service that allows you to upload a new
firmware via UART from a host computer.

The bootloader itself is stored in the internal flash memory.

## Building

```bash
git submodule update --recursive --init
make VARIANT=bl_qspiflash
```

Further instructions on flashing, and debugging can be found in the [common
instructions](bl_common.md).
