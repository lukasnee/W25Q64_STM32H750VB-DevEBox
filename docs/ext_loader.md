# `ext_loader`

Special [STM32 External
Loader](https://github.com/STMicroelectronics/stm32-external-loader) firmware
for this board for accessing the on-board W25Q64 QSPI FLASH memory in
[STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html).

I couldn't find any loader for this board with the specific pin configuration,
so I made one. Kudos to [manoloaterol/MCUDEV_DevEBox_H743-W25Q64-EL](https://github.com/manoloaterol/MCUDEV_DevEBox_H743-W25Q64-EL) and [osos11-Git/STM32H743VIT6_Boring_TECH_QSPI](https://github.com/osos11-Git/STM32H743VIT6_Boring_TECH_QSPI) - great sources of knowledge.

## Building

> Prebuilt loader is available in the `.build` folder.

```bash
make VARIANT=ext_loader
mv build/ext_loader.elf build/W25Q64_STM32H750VB-DevEBox.stldr
```

## Usage in CLI

```powershell
STM32_Programmer_CLI.exe --extload build\W25Q64_STM32H750VB-DevEBox.stldr -c port=swd -w <path_to_app_hex> -rst
```

## Installation for Use in STM32CubeProgrammer (GUI)

1. Copy the `.stldr` file to the `ExternalLoader` folder of the
   STM32CubeProgrammer installation directory.

    ```powershell
    cp build\W25Q64_STM32H750VB-DevEBox.stldr C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\ExternalLoader\
    ```

2. Reopen STM32CubeProgrammer and you should see the loader in the list.
