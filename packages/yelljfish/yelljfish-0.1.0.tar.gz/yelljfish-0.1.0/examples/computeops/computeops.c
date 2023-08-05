#include <stdlib.h>
#include <stdio.h>

unsigned long long hsum(unsigned long long);
unsigned long long computeops(unsigned long long, unsigned long long);

unsigned long long hsum(unsigned long long n) {
    return ((n - 1) * n) / 2;
}

unsigned long long computeops(unsigned long long start,
                              unsigned long long runs) {
    if (runs == 0)
        return start;
    else
        return computeops(start + hsum(start), runs - 1);
}

int main(int argc, char *argv[]) {
    printf("%Lu\n", computeops(atoi(argv[1]), atoi(argv[2])));
    return 0;
}
    
