#include "lfsapp/lfsapp.h"

#include "lfs.h"
#include "quadspi.h"

extern QSPI_HandleTypeDef hqspi;

const uint32_t qspi_flash_lfs_partition_base = QSPI_BASE;
const uint32_t qspi_flash_lfs_partition_size = MEMORY_FLASH_SIZE;

int lfs_qspi_flash_read(const struct lfs_config *c, lfs_block_t block,
                        lfs_off_t off, void *buffer, lfs_size_t size)
{
    if (hqspi.State != HAL_QSPI_STATE_BUSY_MEM_MAPPED &&
        HAL_OK != CSP_QSPI_EnableMemoryMappedMode2()) {
        return LFS_ERR_IO;
    }
    const uint32_t address =
        qspi_flash_lfs_partition_base + (block * c->block_size) + off;
    memcpy(buffer, (void *)(address), size);
    return LFS_ERR_OK;
}

int lfs_qspi_flash_prog(const struct lfs_config *c, lfs_block_t block,
                        lfs_off_t off, const void *buffer, lfs_size_t size)
{
    const uint32_t address = (block * c->block_size) + off;
    if (HAL_OK != CSP_QSPI_WriteMemory(buffer, address, size)) {
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}

int lfs_qspi_flash_erase(const struct lfs_config *c, lfs_block_t block)
{
    const uint32_t start_address = (block * c->block_size);
    const uint32_t end_address = start_address + c->block_size - 1;
    if (HAL_OK != CSP_QSPI_EraseSector(start_address, end_address)) {
        return LFS_ERR_IO;
    }
    return LFS_ERR_OK;
}

int lfs_qspi_flash_sync(const struct lfs_config *c)
{
    return LFS_ERR_OK; // no cache, nothing to sync
}

lfs_t lfs;

const struct lfs_config lfs_cfg = {
    .read = lfs_qspi_flash_read,
    .prog = lfs_qspi_flash_prog,
    .erase = lfs_qspi_flash_erase,
    .sync = lfs_qspi_flash_sync,
    .read_size = MEMORY_PAGE_SIZE, // [1 qspi_flash_lfs_partition_size]
    .prog_size = MEMORY_PAGE_SIZE, // [1 MEMORY_PAGE_SIZE]
    .block_size = MEMORY_SECTOR_SIZE,
    .block_count = (qspi_flash_lfs_partition_size / MEMORY_SECTOR_SIZE),
    .cache_size = MEMORY_PAGE_SIZE,
    .lookahead_size = MEMORY_PAGE_SIZE,
    .block_cycles = 500,
};

int lfsapp_init(void)
{
    // mount the filesystem
    volatile int err = lfs_mount(&lfs, &lfs_cfg);

    // reformat if we can't mount the filesystem
    // this should only happen on the first boot
    if (err) {
        err = lfs_format(&lfs, &lfs_cfg);
        if (err) {
            return err;
        }
        err = lfs_mount(&lfs, &lfs_cfg);
    }
    return err;
}

int lfsapp_deinit(void)
{
    return lfs_unmount(&lfs);
}
