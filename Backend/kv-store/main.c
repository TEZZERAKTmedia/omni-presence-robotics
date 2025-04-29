#include "server.h"
#include "store.h"

int main() {
    start_server(12345);
    cleanup_store(); // Free memory on exit
    return 0;
}
