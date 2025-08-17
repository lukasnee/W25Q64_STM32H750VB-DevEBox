# lfsapp - W25Q64 QSPI 8MB FLASH + littlefs
add_library(lfsapp_W25Q64)
target_sources(lfsapp_W25Q64 PRIVATE lfsapp_W25Q64.c)
target_include_directories(lfsapp_W25Q64 PUBLIC include)
target_link_libraries(
  lfsapp_W25Q64
  PUBLIC littlefs
  PRIVATE W25Q64
)
