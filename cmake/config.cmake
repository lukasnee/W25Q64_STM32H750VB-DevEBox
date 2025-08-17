include_guard(GLOBAL)

add_library(STM32H7xx_HAL_conf INTERFACE)
target_compile_definitions(STM32H7xx_HAL_conf INTERFACE STM32H750xx)
target_include_directories(
  STM32H7xx_HAL_conf
  INTERFACE ${CMAKE_SOURCE_DIR}/Core/Inc # stm32h7xx_hal_conf.h
)
