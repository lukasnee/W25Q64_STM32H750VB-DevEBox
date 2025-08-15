include(${CMAKE_CURRENT_LIST_DIR}/arm-none-eabi-gcc.cmake)

set(device_flags "-mcpu=cortex-m7 -mthumb -mfpu=fpv5-d16 -mfloat-abi=hard")

string(APPEND CMAKE_C_FLAGS " ${device_flags}")
string(APPEND CMAKE_CXX_FLAGS " ${device_flags}")
string(APPEND CMAKE_ASM_FLAGS " ${device_flags}")
string(APPEND CMAKE_EXE_LINKER_FLAGS " ${device_flags}")
