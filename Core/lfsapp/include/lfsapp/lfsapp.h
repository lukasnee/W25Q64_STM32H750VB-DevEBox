#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#include "lfs.h"

extern lfs_t lfs;

int lfsapp_init();
int lfsapp_deinit();

#ifdef __cplusplus
}
#endif
