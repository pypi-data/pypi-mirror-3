#!/usr/bin/env python
# -*- coding: utf-8 -*-

def repeat(string, times=2):
    '''repeat string n times

    options:
        -n N, --times N  repeat N times.
    '''

    print string * times

if __name__ == '__main__':
    import clime.now
