# Common Bootloader Instructions

`bl_iram` and `bl_qspiflash` share a common codebase and build system.
Therefore, most of the instructions are the same for both bootloaders.

> [!Attention]
>
> Make sure you have the environment set up correctly as described in the
> [Environment Setup](env_setup.md).

## Flashing Bootloader

Using ST-LINK/V2 via SWD:

```bash
st-flash --format ihex --reset write .build/bl_iram/bl_iram.hex
```

Using J-Link via SWD:

```bash
JLinkExe -CommandFile flash.jlink
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
[launch.json](../.vscode/launch.json) configuration and start debugging by
hitting `F5`.
