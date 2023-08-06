#!/usr/bin/env python
# -*- coding: utf-8 -*-

def repeat(string, times=2):
    '''repeat string n times

    options:
        -n N, --time N  repeat N times.
    '''
    print string * times

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('string', metavar='STRING', type=str)
    parser.add_argument('-n', '--times', dest='times', metavar='N', type=int, default=2, help='repeat N times.')
    args = parser.parse_args()
    repeat(args.string, args.times)

