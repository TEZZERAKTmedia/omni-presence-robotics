#include "store.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

KVPair *table[TABLE_SIZE] = {0};

unsigned int hash(char *key) {
    unsigned int hash = 0;
    while (*key) hash = (hash << 5) + *key++;
    return hash % TABLE_SIZE;
}

void set(char *key, char *value) {
    if (!key || !value) return;

    unsigned int index = hash(key);
    KVPair *entry = table[index];

    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            free(entry->value);
            entry->value = strdup(value);
            return;
        }
        entry = entry->next;
    }

    KVPair *new_entry = malloc(sizeof(KVPair));
    new_entry->key = strdup(key);
    new_entry->value = strdup(value);
    new_entry->next = table[index];
    table[index] = new_entry;
}

char *get(char *key) {
    if (!key) return NULL;

    unsigned int index = hash(key);
    KVPair *entry = table[index];

    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            return entry->value;
        }
        entry = entry->next;
    }

    return NULL;
}

void delete(char *key) {
    if (!key) return;

    unsigned int index = hash(key);
    KVPair *entry = table[index], *prev = NULL;

    while (entry) {
        if (strcmp(entry->key, key) == 0) {
            if (prev) prev->next = entry->next;
            else table[index] = entry->next;
            free(entry->key);
            free(entry->value);
            free(entry);
            return;
        }
        prev = entry;
        entry = entry->next;
    }
}

void cleanup_store() {
    for (int i = 0; i < TABLE_SIZE; ++i) {
        KVPair *entry = table[i];
        while (entry) {
            KVPair *next = entry->next;
            free(entry->key);
            free(entry->value);
            free(entry);
            entry = next;
        }
        table[i] = NULL;
    }
}
