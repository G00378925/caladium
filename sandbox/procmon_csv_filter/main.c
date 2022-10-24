//
//  main.c
//  caladium
//
//  Created by Declan Kelly on 23-10-2022.
//  Copyright © 2022 Declan Kelly. All rights reserved.
//

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <windows.h>

char *load_file(const char *file_location) {
    FILE *file_handle = fopen(file_location, "r");
    if (!file_handle) return NULL;

    fseek(file_handle, 0, SEEK_END);
    long file_size = ftell(file_handle);
    fseek(file_handle, 0, SEEK_SET);

    char *file_data = malloc(file_size + 1);
    fread((void *) file_data, file_size, 1, file_handle);
    file_data[file_size] = '\0';

    fclose(file_handle);
    return file_data;
}

int main(int argc, const char *argv[]) {
    if (argc <= 2)
        return EXIT_FAILURE;

    const char *procmon_csv_location = argv[1];
    int pid = atoi(argv[2]);

    char *procmon_csv_data = load_file(procmon_csv_location);

    char *procmon_csv_tmp_location = malloc(strlen(procmon_csv_data) + 5);
    strcpy(procmon_csv_tmp_location, procmon_csv_location);
    strcat(procmon_csv_tmp_location, ".tmp");

    FILE *tmp_handle = fopen(procmon_csv_tmp_location, "w");
    char *current_record = procmon_csv_data;
    for (int i = 0; current_record = strtok(i == 0 ? "\n" : NULL, current_record); i++) {
    }
    fclose(tmp_handle);

    DeleteFileA(procmon_csv_location);
    MoveFile(procmon_csv_tmp_location, procmon_csv_location);

    free(procmon_csv_tmp_location);
    free(procmon_csv_data);

    return EXIT_SUCCESS;
}

