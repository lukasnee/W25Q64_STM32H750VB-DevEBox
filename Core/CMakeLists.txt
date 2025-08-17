add_library(bl_common)
target_link_libraries(bl_common PUBLIC STM32H7xx_HAL lfsapp_W25Q64 comm min)
target_sources(
  bl_common
  PRIVATE ${CMAKE_SOURCE_DIR}/startup_stm32h750xx.s Src/gpio.c Src/usart.c
          Src/quadspi.c
  INTERFACE Src/main.c
            Src/stm32h7xx_it.c
            Src/syscalls.c
            Src/stm32h7xx_hal_msp.c
            Src/system_stm32h7xx.c
)
target_include_directories(bl_common PUBLIC ${PROJECT_SOURCE_DIR} Inc)
target_compile_definitions(bl_common PUBLIC NO_TRANSPORT_PROTOCOL)

add_executable(ext_loader)
target_link_libraries(ext_loader PRIVATE bl_common)
target_compile_definitions(ext_loader PUBLIC VARIANT_EXT_LOADER)
target_sources(ext_loader PRIVATE Src/Dev_Inf.c Src/Loader_Src.c Src/sysmem.c)
target_link_options(
  ext_loader PRIVATE -T${PROJECT_SOURCE_DIR}/linker/ext_loader.ld
)
generate_firmware_artifacts(ext_loader)
file(RELATIVE_PATH dir ${PROJECT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR})
add_custom_command(
  TARGET ext_loader
  POST_BUILD
  COMMAND cp ${CMAKE_CURRENT_BINARY_DIR}/ext_loader
          ${CMAKE_CURRENT_BINARY_DIR}/STM32H7-DevEBox.stldr
  COMMAND echo "Generated STM32 External Loader: ${dir}/STM32H7-DevEBox.stldr"
)

add_executable(bl_qspiflash)
target_link_libraries(bl_qspiflash PRIVATE bl_common)
target_compile_definitions(bl_qspiflash PUBLIC VARIANT_BL_QSPIFLASH)
target_link_options(
  bl_qspiflash PRIVATE -T${PROJECT_SOURCE_DIR}/linker/bl_qspiflash.ld
)
generate_firmware_artifacts(bl_qspiflash)

add_executable(bl_iram)
target_link_libraries(bl_iram PRIVATE bl_common)
target_compile_definitions(bl_iram PUBLIC VARIANT_BL_IRAM)
target_sources(bl_iram PRIVATE)
target_link_options(bl_iram PRIVATE -T${PROJECT_SOURCE_DIR}/linker/bl_iram.ld)
generate_firmware_artifacts(bl_iram)
