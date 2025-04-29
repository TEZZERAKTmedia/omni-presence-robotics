#include "server.h"
#include "store.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define BACKLOG 5
#define MAX_KEY_LEN 256
#define MAX_VALUE_LEN 1024

int start_server(int port) {
    int server_fd, client_fd;
    struct sockaddr_in address;
    char buffer[2048];
    socklen_t addrlen = sizeof(address);

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, BACKLOG) < 0) {
        perror("Listen failed");
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d...\n", port);

    while ((client_fd = accept(server_fd, (struct sockaddr *)&address, &addrlen)) >= 0) {
        printf("Accepted a connection!\n");

        int valread;
        while ((valread = read(client_fd, buffer, sizeof(buffer) - 1)) > 0) {
            buffer[valread] = '\0';
            printf("Received: %s\n", buffer);

            char *command = strtok(buffer, " ");
            if (command && strcmp(command, "SET") == 0) {
                char *key = strtok(NULL, " ");
                char *value = strtok(NULL, "\n");

                if (key && value) {
                    if (strlen(key) > MAX_KEY_LEN || strlen(value) > MAX_VALUE_LEN) {
                        write(client_fd, "ERROR: Key or value too long\n", 30);
                        continue;
                    }
                    set(key, value);
                    write(client_fd, "OK\n", 3);
                } else {
                    write(client_fd, "ERROR: Invalid SET\n", 19);
                }

            } else if (command && strcmp(command, "GET") == 0) {
                char *key = strtok(NULL, "\n");

                if (key) {
                    if (strlen(key) > MAX_KEY_LEN) {
                        write(client_fd, "ERROR: Key too long\n", 21);
                        continue;
                    }
                    char *result = get(key);
                    if (result) {
                        write(client_fd, result, strlen(result));
                        write(client_fd, "\n", 1);
                    } else {
                        write(client_fd, "NULL\n", 5);
                    }
                } else {
                    write(client_fd, "ERROR: Invalid GET\n", 19);
                }

            } else if (command && strcmp(command, "DELETE") == 0) {
                char *key = strtok(NULL, "\n");

                if (key) {
                    if (strlen(key) > MAX_KEY_LEN) {
                        write(client_fd, "ERROR: Key too long\n", 21);
                        continue;
                    }
                    delete(key);
                    write(client_fd, "DELETED\n", 8);
                } else {
                    write(client_fd, "ERROR: Invalid DELETE\n", 23);
                }

            } else {
                write(client_fd, "ERROR: Unknown command\n", 24);
            }
        }

        close(client_fd);
    }

    return 0;
}
