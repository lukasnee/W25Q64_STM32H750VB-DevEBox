
# W25Q64_STM32H750VB-DevEBox

![W25Q64_STM32H750VB-DevEBox board](docs/W25Q64_STM32H750VB-DevEBox.jpg)

---

This is an experimental project aimed to unleash the full potential of a cheap
STM32H750VB-DevEBox development board with W25Q64 QSPI FLASH and be a great
platform for any kind of embedded project. The project is in the early stage and
still finding its shape. It incorporates and demonstrates some great open-source
libraries that you can find referenced below.

> Project is developed on WSL Ubuntu.

## Features

- `comm`: A simple Point-to-Point communication protocol for accessing the
  on-board QSPI FLASH via UART from a host computer in Python. `comm` is based
  on the [`min`](https://github.com/min-protocol/min) and
  [`nanopb`](https://github.com/nanopb/nanopb).
- [`bl_iram`](docs/bl_iram.md): Bootloader that loads a program from the QSPI
  flash to the internal D1 domain 512 KiB AXI-SRAM and executes it. Bootloader
  on startup runs the `comm` service that allows you to upload a new firmware
  via UART from a host computer.
- [`bl_qspiflash`](docs/bl_qspiflash.md): Bootloader that Executes In Place
  (XIP) program stored on QSPI flash memory. Bootloader on startup runs the
  `comm` service that allows you to upload a new firmware via UART from a host
  computer.
- [`ext_loader`](docs/ext_loader.md): Special [STM32 External
  Loader](https://github.com/STMicroelectronics/stm32-external-loader) firmware
  for this board for accessing the on-board W25Q64 QSPI FLASH memory in
  [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html).

## TODO

- Generalize and extract the `comm` service to a separate library.
- Add [littlefs](https://github.com/littlefs-project/littlefs) to `bl_iram`
  bootloader where the QSPI FLASH is used as a file system. You can access the
  file system via the `comm` interface (UART). The bootloader expects a file
  `app.bin` in the root directory of the file system. The bootloader will load
  the file to the internal RAM and execute it.
- Use CMake for building the project rather than Makefile.
- `bl_iram` and `bl_qspiflash` tests with simple demo application binaries.
- Add example `.ld` linker scripts for `bl_iram` and `bl_qspiflash`
  applications.
- Add copies of datasheet PDFs of MCU and QSPI FLASH to the `docs` folder.
- Pick a better name for the project.

# References

- [stm32-base STM32H750VB-DevEBox](https://stm32-base.org/boards/STM32H750VBT6-STM32H7XX-M.html#W25Q64JV)
