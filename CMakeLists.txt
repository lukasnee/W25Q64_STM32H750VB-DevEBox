cmake_minimum_required(VERSION 3.16)

project(STM32H7-DevEBox LANGUAGES C CXX ASM)

set(CMAKE_C_STANDARD 23)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_compile_options(-Wall -Wextra -Werror)

if(PROJECT_IS_TOP_LEVEL)
  include(cmake/config.cmake)
endif()

add_subdirectory(extern/ln)

add_subdirectory(Drivers/CMSIS)
add_subdirectory(Drivers/STM32H7xx_HAL_Driver)

# The W25Q64 QSPI 8MB FLASH driver
add_library(W25Q64)
target_sources(W25Q64 PRIVATE Core/Src/quadspi.c)
target_include_directories(W25Q64 PUBLIC Core/Inc # quadspi.h
)
target_link_libraries(W25Q64 PUBLIC CMSIS STM32H7xx_HAL)

add_subdirectory(Core/lfsapp)

if(PROJECT_IS_TOP_LEVEL)
  add_subdirectory(Core/comm)
  add_subdirectory(extern/min)
  target_compile_options(min PRIVATE -Wno-type-limits)
  add_subdirectory(Core)
endif()
