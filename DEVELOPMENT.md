# Development Guide

Make sure you have the right [Development Environment](docs/dev_env.md). Once
that is covered, you can build all bootloaders with a single CMake workflow
command:

```bash
cmake --workflow STM32H7-DevEBox-dbg
```

Next, see the bootloader-specific documentation:

- [`bl_iram`](docs/bl_iram.md).
- [`bl_qspiflash`](docs/bl_qspiflash.md).
- [`ext_loader`](docs/ext_loader.md).

The rest of the sections below are common for all bootloaders.

## Flashing Bootloader

Using ST-LINK/V2 via SWD:

```bash
st-flash --format ihex --reset write .build/Core/<BOOTLOADER_NAME>.hex

```

Using J-Link via SWD:

```bash
JLinkExe -CommandFile flash.<BOOTLOADER_NAME>.jlink
```

## Uploading Application Firmware

Reset the board and within 3 seconds run the following command:

```bash
.venv/bin/python3 tools/comm/comm.py upload_app <fw_path>
```

> E.g.: `.venv/bin/python3 tools/comm/comm.py upload_app
> ../m8ec/.build/platform/STM32H750/STM32H750.bin`

If you have an SWD debugger connected to the board with a reset pin, you can run
this without the need to reset the board:

```bash
st-flash reset && sleep 1 && .venv/bin/python3 tools/comm/comm.py upload_app <fw_path>
```

> E.g.: `st-flash reset && sleep 1 && .venv/bin/python3 tools/comm/comm.py
> upload_app ../m8ec/.build/platform/STM32H750/STM32H750.bin`

## Debugging in VSCode

You can debug your application together with the bootloader in VSCode using
ST-LINK/V2 via SWD, openOCD and `cortex-debug` extension. Add your application
ELF path to the `symbolFiles` list of the `bl_iram`
[launch.json](.vscode/launch.json) configuration and start debugging by
hitting `F5`.
