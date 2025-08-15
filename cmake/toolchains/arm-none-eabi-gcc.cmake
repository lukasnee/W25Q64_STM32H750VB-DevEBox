set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR ARM)
set(CMAKE_CROSSCOMPILING TRUE)

set(toolchain_prefix "arm-none-eabi-")
find_program(toolchain_gcc_path ${toolchain_prefix}gcc)
if(NOT toolchain_gcc_path)
  message(
    FATAL_ERROR
      "Could not find ${toolchain_prefix}gcc. Please ensure the ARM GCC toolchain is installed and in your PATH."
  )
endif()

get_filename_component(arm_toolchain_dir ${toolchain_gcc_path} DIRECTORY)

set(CMAKE_C_COMPILER ${arm_toolchain_dir}/${toolchain_prefix}gcc)
set(CMAKE_CXX_COMPILER ${arm_toolchain_dir}/${toolchain_prefix}g++)
set(CMAKE_ASM_COMPILER ${arm_toolchain_dir}/${toolchain_prefix}gcc)
set(CMAKE_AR ${arm_toolchain_dir}/${toolchain_prefix}ar)
set(CMAKE_OBJCOPY
    ${arm_toolchain_dir}/${toolchain_prefix}objcopy
    CACHE INTERNAL "objcopy tool"
)
set(CMAKE_OBJDUMP
    ${arm_toolchain_dir}/${toolchain_prefix}objdump
    CACHE INTERNAL "objdump tool"
)
set(CMAKE_NM
    ${arm_toolchain_dir}/${toolchain_prefix}nm
    CACHE INTERNAL "nm tool"
)
set(CMAKE_SIZE_UTIL
    ${arm_toolchain_dir}/${toolchain_prefix}size
    CACHE INTERNAL "size tool"
)

set(CMAKE_FIND_ROOT_PATH ${arm_toolchain_dir})
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

set(CMAKE_C_COMPILER_WORKS 1)
set(CMAKE_CXX_COMPILER_WORKS 1)

set(compiler_flags "-fstack-usage -fdata-sections -ffunction-sections -g")

string(APPEND CMAKE_C_FLAGS " ${compiler_flags}")
string(APPEND CMAKE_CXX_FLAGS
       " ${compiler_flags} -fno-rtti -fno-exceptions -fno-threadsafe-statics"
)
string(APPEND CMAKE_ASM_FLAGS " ${compiler_flags} -x assembler-with-cpp")
string(
  APPEND
  CMAKE_EXE_LINKER_FLAGS
  " --specs=nosys.specs -static -Wl,--gc-sections -Wl,--print-memory-usage -u _printf_float -Wl,--start-group -lc -lm -lstdc++ -lsupc++ -Wl,--end-group"
  # -Wl,--verbose -Wl,--trace
)

# https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html
# https://gcc.gnu.org/onlinedocs/gcc/Debugging-Options.html

set(compiler_flags_debug " -gdwarf-2 -Og")
set(CMAKE_C_FLAGS_DEBUG_INIT ${compiler_flags_debug})
set(CMAKE_CXX_FLAGS_DEBUG_INIT ${compiler_flags_debug})
set(CMAKE_ASM_FLAGS_DEBUG_INIT ${compiler_flags_debug})

set(compiler_flags_release " -O1")
set(CMAKE_C_FLAGS_RELEASE_INIT ${compiler_flags_release})
set(CMAKE_CXX_FLAGS_RELEASE_INIT ${compiler_flags_release})
set(CMAKE_ASM_FLAGS_RELEASE_INIT ${compiler_flags_release})

function(generate_firmware_artifacts exec_target_name)
  target_link_options(
    ${exec_target_name} PUBLIC
    -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/${exec_target_name}.map -Wl,--cref
  )
  file(RELATIVE_PATH dir ${PROJECT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR})
  add_custom_command(
    TARGET ${exec_target_name}
    POST_BUILD
    COMMAND arm-none-eabi-size ${exec_target_name}
    COMMAND echo "Generating firmware artifacts:"
    COMMAND echo "${dir}/${exec_target_name}.map"
    COMMAND ${CMAKE_OBJCOPY} -O ihex ${exec_target_name} ${exec_target_name}.hex
    COMMAND echo "${dir}/${exec_target_name}.hex"
    COMMAND ${CMAKE_OBJCOPY} -O binary ${exec_target_name}
            ${exec_target_name}.bin
    COMMAND echo "${dir}/${exec_target_name}.bin"
    COMMAND ${CMAKE_OBJDUMP} -S -t ${exec_target_name} >
            ${exec_target_name}.dump
    COMMAND echo "${dir}/${exec_target_name}.dump"
    COMMAND ${CMAKE_NM} ${exec_target_name} -C -n -S -s >
            ${exec_target_name}.address-sort.nm
    COMMAND echo "${dir}/${exec_target_name}.address-sort.nm"
    COMMAND ${CMAKE_NM} ${exec_target_name} -C -S -s --size-sort >
            ${exec_target_name}.size-sort.nm
    COMMAND echo "${dir}/${exec_target_name}.size-sort.nm"
    COMMAND ${CMAKE_NM} -lnC ${exec_target_name} > ${exec_target_name}.symbols
    COMMAND echo "${dir}/${exec_target_name}.symbols"
  )
endfunction()
