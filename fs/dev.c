#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>

#include "dev.h"

static int fd = -1;
static int blk_size = -1;
static int blk_count = -1;

int dev_init() {
    if ((fd = open("dev.bin", O_RDWR)) == -1) return -1;

    struct stat statbuf;
    if (fstat(fd, &statbuf) != 0) return -1;
    blk_size    = statbuf.st_blksize;
    blk_count   = (statbuf.st_blocks * 512) / blk_size;

    return fd;
}

int dev_size() {
    return blk_size;
}

int dev_count() {
    return blk_count;
}

int dev_read(int id, unsigned char* buf) {
    if (lseek(fd, blk_size * id, SEEK_SET) == -1) return -1;
    if (read(fd, buf, blk_size) != blk_size) return -1;
    return 0;
}

int dev_write(int id, unsigned char* buf) {
    if (lseek(fd, blk_size * id, SEEK_SET) == -1) return -1;
    if (write(fd, buf, blk_size) != blk_size) return -1;
    return 0;
}

