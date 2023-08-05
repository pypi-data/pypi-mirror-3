#!/usr/bin/env python3

hsum = lambda n: ((n - 1) * n) // 2
computeops = lambda start, runs: start if runs == 0 \
    else computeops(start + hsum(start), runs - 1)

if __name__ == '__main__':
    import sys
    print(computeops(*map(int, sys.argv[1:3])))
