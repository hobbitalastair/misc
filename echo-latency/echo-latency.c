/* echo-latency.c
 *
 * Experiment to see how bad a round trip through another process is on the
 * Toshiba, especially for interactive use.
 *
 * Based on some basic evidence, it looks like the worst case is likely to be around
 * 16msec for a round trip, with timing for recieving back and writing out being
 * at most 8msec and more typically ~1msec.
 *
 * Author:  Alastair Hughes
 * Contact: hobbitalastair at yandex dot com
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>

void loopback() {
    /* Loop stdin back into stdout */

    char c = {0};
    errno = 0;
    while (read(0, &c, 1) == 1 && write(1, &c, 1) == 1);
    if (errno != 0) fprintf(stderr, "read/write %d: %s\n", __LINE__, strerror(errno));
}

void passthrough(int input, int output) {
    /* Print newlines to input, and feed output through to stdout.
     *
     * We assume that we will get exactly one character back for each character
     * we feed in.
     */
    while (1) {
        char c = '\n';
        struct timespec ts1;
        if (clock_gettime(CLOCK_REALTIME, &ts1) != 0) {
            fprintf(stderr, "clock_gettime: %s\n", strerror(errno));
        }
        if (write(input, &c, 1) != 1) {
            fprintf(stderr, "read/write %d: %s\n", __LINE__, strerror(errno));
            return;
        }
        if (!(read(output, &c, 1) == 1 && write(1, &c, 1) == 1)) {
            fprintf(stderr, "read/write %d: %s\n", __LINE__, strerror(errno));
            return;
        }
        struct timespec ts2;
        if (clock_gettime(CLOCK_REALTIME, &ts2) != 0) {
            fprintf(stderr, "clock_gettime: %s\n", strerror(errno));
        }
        fprintf(stderr, "latency (nanoseconds): %ld\n", ts2.tv_nsec - ts1.tv_nsec);
    }
}

int main(int argc, char** argv) {
    int leg1[2] = {0};
    int leg2[2] = {0};
    
    if (!(pipe(leg1) == 0 && pipe(leg2) == 0)) {
        fprintf(stderr, "pipe: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }

    pid_t pid = fork();
    if (pid == 0) {
        close(leg1[1]);
        close(leg2[0]);
        if (!(dup2(leg1[0], 0) != -1 && dup2(leg2[1], 1) != -1)) {
            fprintf(stderr, "dup2: %s\n", strerror(errno));
            exit(EXIT_FAILURE);
        }

        loopback();
    } else if (pid > 0) {
        close(leg1[0]);
        close(leg2[1]);
        passthrough(leg1[1], leg2[0]);
    } else {
        fprintf(stderr, "fork: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }
}
