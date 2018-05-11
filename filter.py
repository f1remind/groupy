#!/usr/bin/env python3

def main():
    info = []
    with open('output.txt') as f:
        info = [e.strip().split(',') for e in f.readlines()]
        info = [[e[0],int(e[1])] for e in info]
        info = sorted(info, key=lambda x: x[1])

    for e in info:
        if e[1] > 50000:
            print('https://' + e[0])

if __name__ == '__main__':
    main()
