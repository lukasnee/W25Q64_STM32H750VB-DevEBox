cmake_minimum_required(VERSION 3.16)

project(W25Q64_STM32H750VB-DevEBox)

# Currently the intended way of building this project is using makefile. Some
# parts of the project can be built using CMake as libraries for external use.
# TODO: migrate the project to CMake completely.

add_subdirectory(Drivers/CMSIS)
add_subdirectory(Drivers/STM32H7xx_HAL_Driver)

# The littlefs library. TODO: improve modularity: fork littlefs, create a
# CMakeLists.txt, extract the following CMake code to it, and add it as a
# subdirectory.
add_library(littlefs)
target_sources(
  littlefs PRIVATE extern/littlefs/lfs.c extern/littlefs/lfs_util.c
)
target_include_directories(littlefs PUBLIC extern/littlefs)

# The W25Q64 QSPI 8MB FLASH driver
add_library(W25Q64)
target_sources(W25Q64 PRIVATE Core/Src/quadspi.c)
target_include_directories(W25Q64 PUBLIC Core/Inc # quadspi.h
)
target_link_libraries(W25Q64 PUBLIC CMSIS STM32H7xx_HAL)

# lfsapp - W25Q64 QSPI 8MB FLASH + littlefs
add_library(littlefs_W25Q64)
target_sources(littlefs_W25Q64 PRIVATE Core/lfsapp/lfsapp.c)
target_include_directories(littlefs_W25Q64 PUBLIC Core/lfsapp/include)
target_link_libraries(
  littlefs_W25Q64
  PUBLIC littlefs
  PRIVATE W25Q64
)
