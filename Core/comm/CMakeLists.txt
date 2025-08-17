
add_library(comm)

target_sources(comm PRIVATE comm.cpp)
target_include_directories(comm PUBLIC include)

set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/extern/nanopb/extra)
find_package(Nanopb REQUIRED)
nanopb_generate_cpp(TARGET comm_proto comm.proto)

target_link_libraries(comm PRIVATE comm_proto STM32H7xx_HAL lfsapp_W25Q64 min)
