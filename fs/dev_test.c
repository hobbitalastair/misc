#include <stdio.h>
#include <stdlib.h>

#include "dev.h"

int main(void) {
    if (dev_init() == -1) {
        printf("dev_init failed\n");
    }

    printf("Size: %d\n", dev_size());
    printf("Count: %d\n", dev_count());
    printf("Bytes: %d\n", dev_count()*dev_size());

    unsigned char buf[dev_size()];
    for (int k = 0; k < dev_size(); k++) {
        buf[k] = 'a';
    }

    for (int i = 0; i < dev_count(); i++) {
        dev_write(i, buf);
    }

    for (int i = 0; i < dev_count(); i++) {
        dev_read(i, buf);
        for (int k = 0; k < dev_size(); k++) {
            if (buf[k] != 'a') {
                printf("expected 'a', got %c\n", buf[k]);
            }
        }
    }

}
