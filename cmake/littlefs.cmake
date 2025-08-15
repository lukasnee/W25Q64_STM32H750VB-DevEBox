# TODO: improve modularity: fork littlefs, create a CMakeLists.txt, extract the
# following CMake code to it, and add it as a subdirectory.
add_library(littlefs)
target_sources(
  littlefs PRIVATE extern/littlefs/lfs.c extern/littlefs/lfs_util.c
)
target_compile_options(littlefs PRIVATE $<$<CONFIG:Release>: -DLFS_NO_ASSERT>)
  
target_include_directories(littlefs PUBLIC extern/littlefs)
