#include <stdio.h>
#include <stdlib.h>

void matrix_multiplication(int *a, int *b, int *output, int i,
                           int k, int j) {
    // 1*k temperal array
    int *ytemp_row = (int *)malloc(k * sizeof(int));

    for (int y = 0; y < j; y++) {

            for (int z = 0;z < k; z++) {
                ytemp_row[z] = b[z * j + y];
            }
        for (int x = 0; x < i; x++) {
            int sum = 0;
            for (int z = 0; z < k; z++) {
                sum += a[x * k + z] * ytemp_row[z];
            }
            output[x * j + y] = sum;
        }
    }

    free(ytemp_row);
    return;
}

// #include <stdio.h>
// #include <stdlib.h>

// void matrix_multiplication(int *a, int *b, int *output, int i,
//                            int k, int j) {
//     // 1*k temperal array
//     int *temp_row = (int *)malloc(k * sizeof(int));

//     for (int x = 0; x < i; x++) {

//         for (int z = 0; z < k; z++) {
//             temp_row[z] = a[x * k + z];
//         }

//         for (int y = 0; y < j; y++) {
//             int sum = 0;
//             for (int z = 0; z < k; z++) {
//                 sum += temp_row[z] * b[z * j + y];
//             }
//             output[x * j + y] = sum;
//         }
//     }

//     free(temp_row);
//     return;
// }