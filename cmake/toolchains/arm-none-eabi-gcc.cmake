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

set(compiler_flags
    "--specs=nosys.specs -fstack-usage -fdata-sections -ffunction-sections -g"
)

set(CMAKE_C_FLAGS " ${compiler_flags}")
set(CMAKE_CXX_FLAGS
    " ${compiler_flags} -fno-rtti -fno-exceptions -fno-threadsafe-statics"
)
set(CMAKE_ASM_FLAGS " ${compiler_flags} -x assembler-with-cpp")
set(CMAKE_EXE_LINKER_FLAGS
    " -static -Wl,--gc-sections -Wl,--print-memory-usage -u _printf_float -Wl,--start-group -lc -lm -lstdc++ -lsupc++ -Wl,--end-group"
    # -Wl,--verbose -Wl,--trace -u _scanf_float
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

function(generate_firmware_artifacts fw_target)
  target_link_options(
    ${fw_target}
    PUBLIC
    -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/${fw_target}.map
    -Wl,--cref
    -Wl,--no-warn-rwx-segment
  )

  file(RELATIVE_PATH dir ${PROJECT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR})
  add_custom_command(
    TARGET ${fw_target}
    POST_BUILD
    COMMAND arm-none-eabi-size ${fw_target}
    COMMAND echo "Generating firmware artifacts:"
    COMMAND echo "${dir}/${fw_target}.map"
    COMMAND ${CMAKE_OBJCOPY} -O ihex ${fw_target} ${fw_target}.hex
    COMMAND echo "${dir}/${fw_target}.hex"
    COMMAND ${CMAKE_OBJCOPY} -O binary ${fw_target} ${fw_target}.bin
    COMMAND echo "${dir}/${fw_target}.bin"
    COMMAND ${CMAKE_OBJDUMP} -S -t ${fw_target} > ${fw_target}.dump
    COMMAND echo "${dir}/${fw_target}.dump"
    COMMAND ${CMAKE_NM} ${fw_target} -C -n -S -s > ${fw_target}.address-sort.nm
    COMMAND echo "${dir}/${fw_target}.address-sort.nm"
    COMMAND ${CMAKE_NM} ${fw_target} -C -S -s --size-sort >
            ${fw_target}.size-sort.nm
    COMMAND echo "${dir}/${fw_target}.size-sort.nm"
    COMMAND ${CMAKE_NM} -lnC ${fw_target} > ${fw_target}.symbols
    COMMAND echo "${dir}/${fw_target}.symbols"
  )
endfunction()
