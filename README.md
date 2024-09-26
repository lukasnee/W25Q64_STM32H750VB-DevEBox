
![W25Q64_STM32H750VB-DevEBox board](docs/W25Q64_STM32H750VB-DevEBox.jpg)

# About

W25Q64 QSPI FLASH memory STM32H750VB-DevEBox External Loader for STM32CubeProgrammer.

Kudos to [@manoloaterol](https://github.com/manoloaterol) and
[@osos11-Git](https://github.com/osos11-Git) for the external loader knowledge in their open-source projects - see [References](#References).

# Building

> Prebuilt loader is available in the `.build` folder.

```bash
make VARIANT=ext_loader
mv build/ext_loader.elf build/W25Q64_STM32H750VB-DevEBox.stldr
```

## Variants

There are three build variants available:

- `ext_loader` - External loader firmware for use with STM32CubeProgrammer. **This is the default variant.**

- `bl_iram` - Bootloader that loads a program from the QSPI flash to the internal RAM and executes it.

- `bl_qspiflash` - Bootloader that Executes In Place (XIP) program that is stored in QSPI flash memory.

## Variant ``ext_loader``

### Installation

1. Copy the `.stldr` file to the `ExternalLoader` folder of the STM32CubeProgrammer installation directory.

    ```
    cp build\W25Q64_STM32H750VB-DevEBox.stldr C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\ExternalLoader\
    ```

2. Reopen STM32CubeProgrammer and you should see the loader in the list.

## Variant ``bl_iram``

### Prerequisites

```bash
sudo apt-get update && sudo apt-get -y upgrade
pip install protobuf==3.20.*
```

### Building

```bash
git submodule update --recursive --init
make VARIANT=bl_iram
```

### Flashing

```bash
st-flash --format ihex --reset write .build/bl_iram/bl_iram.hex
```

### Flashing firmware to QSPI FLASH

```bash
```

### Debugging

The firmware can be debugged in VSCode using ST-LINK/V2 debugger via SWD, openOCD and `cortex-debug` extension. Modify `bl_iram` target in [launch.json](.vscode/launch.json) as needed and start debugging.

## Variant ``bl_qspiflash``

TODO: instructions

## References

- Part of the project (`VARIANT=ext_loader`) based on: [manoloaterol/MCUDEV_DevEBox_H743-W25Q64-EL](https://github.com/manoloaterol/MCUDEV_DevEBox_H743-W25Q64-EL)
- A good knowledge source: [osos11-Git/STM32H743VIT6_Boring_TECH_QSPI](https://github.com/osos11-Git/STM32H743VIT6_Boring_TECH_QSPI)
