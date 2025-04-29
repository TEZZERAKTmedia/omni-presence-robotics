CC=gcc
CFLAGS=-Wall

all: kvstore

kvstore: main.c server.c store.c utils.c
	$(CC) $(CFLAGS) main.c server.c store.c utils.c -o kvstore

clean:
	rm -f kvstore
