add_library(CMSIS INTERFACE)

target_include_directories(CMSIS INTERFACE Device/ST/STM32H7xx/Include Include)

if(SEGGER_SYSVIEW_ENABLED)
  target_compile_options(
    CMSIS
    INTERFACE
      -finstrument-functions
      -finstrument-functions-exclude-file-list=Include/cmsis_gcc.h,Include/core_cm7.h
  )
endif()
