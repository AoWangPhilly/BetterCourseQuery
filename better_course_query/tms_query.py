# !/usr/bin/env python

from __future__ import print_function, unicode_literals
import pandas as pd
import numpy as np
import os
import glob
from pprint import pprint
from PyInquirer import prompt, print_json


# class TMSQuery():
#     def __init__(self):
#         pass

#     def get_professor(self):
#         pass

#     def get_credit(self):
#         pass

#     def get_no_prereqs(self):
#         pass

#     def get_course(self):
#         pass

#     def get_crn(self):
#         pass

#     def print_results(self):
#         pass


# if __name__ == '__main__':
#     # fall = os.path.join('DREXEL', 'FALL', 'Col of Computing & Informatics', 'CS.csv')
#     # df = pd.read_csv(fall);

#     # print(df)


questions = [
    {
        'type': 'list',
        'choices': ['FALL', 'WINTER', 'SPRING', 'SUMMER'],
        'name': 'quarter',
        'message': 'Select a quarter:',
    },
    {
        'type': 'list',
        'choices': ['Subject Code & Course No.', 'CRN #', 'Professor', 'No. of Credits', 'Prequisites'],
        'name': 'find_by',
        'message': 'Find course by: '
    },
    {
        'type': 'input',
        'name': 'Subject Code & Course No.',
        'message': 'Enter Subject Code & Course No.: i.e. CS 265',
        'when': lambda answers: answers['find_by'] == 'Subject Code & Course No.'
    },
    {
        'type': 'input',
        'name': 'CRN #',
        'message': 'Enter CRN #: ',
        'when': lambda answers: answers['find_by'] == 'CRN #'
    },
    {
        'type': 'input',
        'name': 'Professor',
        'message': 'Enter Professor\'s name',
        'when': lambda answers: answers['find_by'] == 'Professor'
    },
    {
        'type': 'input',
        'name': 'No. of Credits',
        'message': 'Enter No. of Credits',
        'when': lambda answers: answers['find_by'] == 'No. of Credits '
    }
]

answers = prompt(questions)
pprint(answers)  # use the answers as input for your app
