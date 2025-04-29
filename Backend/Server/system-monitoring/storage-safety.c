// system_monitor.c
#include <stdio.h>
#include <stdlib.h>
#include <sys/statvfs.h>
#include <string.h>

void check_disk_space() {
    struct statvfs stat;

    if (statvfs("/", &stat) != 0) {
        perror("statvfs");
        exit(1);
    }

    unsigned long total = stat.f_blocks * stat.f_frsize;
    unsigned long free = stat.f_bfree * stat.f_frsize;
    float percent_free = (free * 100.0) / total;

    printf("{\"disk_free_percent\": %.2f}\n", percent_free);

    if (percent_free < 5.0) {
        fprintf(stderr, "[WARNING] Low disk space: %.2f%% free\n", percent_free);
        exit(2);
    }

    exit(0);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s check_disk\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "check_disk") == 0) {
        check_disk_space();
    } else {
        fprintf(stderr, "Unknown command: %s\n", argv[1]);
        return 1;
    }

    return 0;
}
