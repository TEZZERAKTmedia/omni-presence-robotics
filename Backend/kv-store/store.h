#ifndef STORE_H
#define STORE_H

#define TABLE_SIZE 256

typedef struct KVPair {
    char *key;
    char *value;
    struct KVPair *next;
} KVPair;

void set(char *key, char *value);
char *get(char *key);
void delete(char *key);
unsigned int hash(char *key);
void cleanup_store();

#endif
