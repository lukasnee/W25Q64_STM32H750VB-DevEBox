# Common Bootloader Instructions

`bl_iram` and `bl_qspiflash` share a common codebase and build system.
Therefore, most of the instructions are the same for both bootloaders.

## Prerequisites

```bash
sudo apt-get update && sudo apt-get -y upgrade
pip install protobuf==3.20.*
```

## Flashing Bootloader

```bash
st-flash --format ihex --reset write .build/bl_iram/bl_iram.hex
```

## Flashing Application

Reset the board and within 3 seconds run the following command:

```bash
python3 tools/comm/comm.py <app_bin>
```

> E.g.: `python3 tools/comm/comm.py
> ../m8ec/.build/platform/STM32H750/STM32H750.bin`

If you have an SWD debugger connected to the board with a reset pin, you can run
this without the need to reset the board:

```bash
st-flash reset && sleep 1 && python3 tools/comm/comm.py <app_bin>
```

> E.g.: `st-flash reset && sleep 1 && python3 tools/comm/comm.py
> ../m8ec/.build/platform/STM32H750/STM32H750.bin`

## Debugging in VSCode

You can debug your application together with the bootloader in VSCode using
ST-LINK/V2 via SWD, openOCD and `cortex-debug` extension. Add your application
ELF path to the `symbolFiles` list of the `bl_iram`
[launch.json](../.vscode/launch.json) configuration and start debugging by
hitting `F5`.
