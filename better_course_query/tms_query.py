# !/usr/bin/env python
'''
file: term_query.py
author: ao wang
date: 12/29/25
brief:
'''
from __future__ import print_function, unicode_literals
import pandas as pd
import numpy as np
from os.path import join
from glob import glob
from pprint import pprint
from PyInquirer import prompt, print_json
from tabulate import tabulate
import textwrap
from art import tprint
import shutil


class color:
    '''

    '''
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def bolden_blue(title: str) -> str:
    '''

    '''
    return color.BOLD + color.BLUE + color.UNDERLINE + title + color.END


def indent(text, amount, ch=' '):
    '''


    '''
    return "\n" + textwrap.indent(text, amount * ch)


class TMSQuery():
    '''

    '''

    def __init__(self):
        self.query_df = pd.DataFrame()
        questions = [
            {
                'type': 'list',
                'choices': ['FALL', 'WINTER', 'SPRING', 'SUMMER'],
                'name': 'quarter',
                'message': 'Select a quarter:',
            },
            {
                'type': 'input',
                'name': 'CRN',
                'message': 'Enter CRN No.: '
            },
        ]
        self.answers = prompt(questions)
        self.colleges = glob(join('DREXEL', self.answers['quarter'], '*/'))

    def start(self):
        # A Course Reference Number (CRN) is a unique 5 digit identifier assigned to a class for registration purposes
        if self.answers['CRN']:
            self.query_df = self.get_crn()
        else:
            courses = [
                {
                    'type': 'input',
                    'name': 'Subject Code',
                    'message': 'Enter Subject Code: '
                },
                {
                    'type': 'input',
                    'name': 'Course No.',
                    'message': 'Enter Course No.: ',
                    'when': lambda answers: answers['Subject Code'] != ''
                }
            ]
            answers = prompt(courses)

            if answers['Subject Code']:
                self.query_df = self.get_course_by_subject(answers['Course No.'])

        output = prompt({
            'type': 'confirm',
            'message': 'Want to save the query? ',
            'name': 'save',
            'default': False,
        })

        if output['save']:
            self.query_df.to_csv('saved_query.csv')
            print(bolden_blue('SUCESSFUL! Query saved >:D'))

    def get_crn(self):
        crn = self.answers['CRN']
        for college in self.colleges:
            majors = glob(join(college, '*.csv'))
            for major in majors:
                crn_df = pd.read_csv(major)
                df['CRN'] = crn_df['CRN'].astype(str)
                if crn_df['CRN'].str.contains(crn).any():
                    return crn_df[(crn_df['CRN'] == crn) & (crn_df['No. of Avail. Seats'] != 0)]
    
    def get_course_by_subject(self, course_no=False):
        subject = self.answers['Subject Code']
        for college in self.colleges:
            majors = glob(join(college, '*.csv'))
            for major in majors:
                if subject == major:
                    course_df = pd.read_csv(major)
                    if course_no: course_df = course_df[course_df['Course No.'] == course_no]
        return course_df

if __name__ == '__main__':
    tprint('Better Course Query'.center(shutil.get_terminal_size().columns//2))

    query = TMSQuery()
    print()
    query.start()
