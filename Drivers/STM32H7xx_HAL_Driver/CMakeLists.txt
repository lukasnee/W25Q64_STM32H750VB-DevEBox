add_library(STM32H7xx_HAL)

target_sources(
  STM32H7xx_HAL
  PRIVATE Src/stm32h7xx_hal_hcd.c
          Src/stm32h7xx_ll_usb.c
          Src/stm32h7xx_hal_rcc.c
          Src/stm32h7xx_hal_rcc_ex.c
          Src/stm32h7xx_hal_flash.c
          Src/stm32h7xx_hal_flash_ex.c
          Src/stm32h7xx_hal_gpio.c
          Src/stm32h7xx_hal_hsem.c
          Src/stm32h7xx_hal_dma.c
          Src/stm32h7xx_hal_dma_ex.c
          Src/stm32h7xx_hal_mdma.c
          Src/stm32h7xx_hal_pwr.c
          Src/stm32h7xx_hal_pwr_ex.c
          Src/stm32h7xx_hal_cortex.c
          Src/stm32h7xx_hal.c
          Src/stm32h7xx_hal_exti.c
          Src/stm32h7xx_hal_i2s.c
          Src/stm32h7xx_hal_i2s_ex.c
          Src/stm32h7xx_hal_spi.c
          Src/stm32h7xx_hal_spi_ex.c
          Src/stm32h7xx_hal_tim.c
          Src/stm32h7xx_hal_tim_ex.c
          Src/stm32h7xx_hal_uart.c
          Src/stm32h7xx_hal_uart_ex.c
          Src/stm32h7xx_hal_qspi.c
)

target_include_directories(STM32H7xx_HAL PUBLIC Inc Inc/Legacy)

target_compile_definitions(
  STM32H7xx_HAL PUBLIC -DUSE_HAL_DRIVER -DSTM32H750xx -DSTM32H7
)

target_compile_options(STM32H7xx_HAL PRIVATE -Wno-unused-parameter)

if(NOT TARGET STM32H7xx_HAL_conf)
  message(FATAL_ERROR "STM32H7xx_HAL_conf not found")
endif()

target_link_libraries(STM32H7xx_HAL PUBLIC CMSIS STM32H7xx_HAL_conf)

if(SEGGER_SYSVIEW_ENABLED)
  target_compile_options(
    STM32H7xx_HAL
    PRIVATE
      -finstrument-functions
      -finstrument-functions-exclude-file-list=Src/stm32h7xx_hal_hcd,Src/stm32h7xx_ll_usb,Src/stm32h7xx_hal_rcc,Src/stm32h7xx_hal_rcc_ex,Src/stm32h7xx_hal_flash,Src/stm32h7xx_hal_flash_ex,Src/stm32h7xx_hal_gpio,Src/stm32h7xx_hal_hsem,Src/stm32h7xx_hal_dma,Src/stm32h7xx_hal_dma_ex,Src/stm32h7xx_hal_mdma,Src/stm32h7xx_hal_pwr,Src/stm32h7xx_hal_pwr_ex,Src/stm32h7xx_hal_cortex,Src/stm32h7xx_hal,Src/stm32h7xx_hal_exti,Src/stm32h7xx_hal_i2s,Src/stm32h7xx_hal_i2s_ex,Src/stm32h7xx_hal_spi,Src/stm32h7xx_hal_spi_ex,Src/stm32h7xx_hal_tim,Src/stm32h7xx_hal_tim_ex,Src/stm32h7xx_hal_uart,Src/stm32h7xx_hal_uart_ex
  )
endif()
