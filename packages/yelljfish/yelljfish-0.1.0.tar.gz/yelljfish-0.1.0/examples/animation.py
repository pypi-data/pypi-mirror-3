#!/usr/bin/env python3

import random
from yelljfish import generate_image

"""
Animates.
"""

def grange():
    return random.randint(2, 32)

def g1():
    return random.choice((-1, 1))

def maybe():
    return random.randint(0, 1) == 1

def animate(outdir, runs=5, numberofpoints=5, width=640, height=480,
            frames=1000):
    size = (width, height)
    t = outdir + '/{:08}.png'
    points = [[random.randrange(0, size[0]), random.randrange(0, size[1]),
               random.randrange(0, 2**32)] for i in range(numberofpoints)]
    moves = [[[g1(), grange()] for i in range(2)] for i in range(5)]
    for i in range(frames):
        print('Generating frame {}...'.format(i))
        generate_image(width=size[0], height=size[1], runs=runs, points=points,
                       out=t.format(i))
        for j in range(numberofpoints):
            for k in range(2):
                if maybe():
                    points[j][k] += moves[j][k][0]
                    if points[j][k] >= size[k]:
                        points[j][k] -= 2
                        moves[j][k][0] = -1
                    elif points[j][k] < 0:
                        points[j][k] += 2
                        moves[j][k][0] = 1
                    moves[j][k][1] -= 1
                    if moves[j][k][1] == 0:
                        moves[j][k] = [-moves[j][k][0], grange()]

if __name__ == '__main__':
    import sys
    animate(sys.argv[1], *map(int, sys.argv[2:]))
