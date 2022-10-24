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

int main(int argc, const char *argv[]) {
    if (argc <= 2)
        return EXIT_FAILURE;

    const char *procmon_csv = argv[1];
    int pid = atoi(argv[2]);

    return EXIT_SUCCESS;
}

