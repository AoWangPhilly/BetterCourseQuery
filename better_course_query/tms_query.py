#!/usr/bin/env python

import pandas as pd
import numpy as np
import os
import glob


class TMSQuery():
    def __init__(self):
        pass

    def get_professor(self):
        pass

    def get_credit(self):
        pass

    def get_no_prereqs(self):
        pass

    def get_course(self):
        pass

    def get_crn(self):
        pass


if __name__ == '__main__':
    # fall = os.path.join('DREXEL', 'FALL', 'Col of Computing & Informatics', 'CS.csv')
    # df = pd.read_csv(fall);

    # print(df)
    import argparse
    parser = argparse.ArgumentParser(description='Add some integers.')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                        help='interger list')
    parser.add_argument('--sum', action='store_const',
                        const=sum, default=max,
                        help='sum the integers (default: find the max)')
    args = parser.parse_args()
    print(args.sum(args.integers))
