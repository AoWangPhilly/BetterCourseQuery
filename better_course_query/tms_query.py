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
from PyInquirer import prompt, print_json, Separator
from tabulate import tabulate
import textwrap
from art import tprint
import shutil
import re


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
                'message': 'Enter CRN No.: ',
                # 'validate': ''
            },
        ]
        self.answers = prompt(questions)
        self.colleges = glob(join('DREXEL', self.answers['quarter'], '*/'))

    def start(self):
        # A Course Reference Number (CRN) is a unique 5 digit identifier assigned to a class for registration purposes
        if self.answers['CRN']:
            self.query_df = self.__get_crn()
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
                self.query_df = self.__get_course_by_subject(answers=answers)

            num_of_credits = {
                'type': 'checkbox',
                'name': 'Credits',
                'message': 'Enter No. of Credits: ',
                'choices': [Separator('---CREDITS---'),
                            {'name': '1.00'},
                            {'name': '2.00'},
                            {'name': '3.00'},
                            {'name': '4.00'}]
            }
            answers = prompt(num_of_credits)

            if answers['Credits']:
                self.query_df = self.__get_num_of_credits(
                    df=self.query_df, answers=answers)

            instructor = {
                'type': 'input',
                'name': 'Instructor',
                'message': 'Enter Instructor\'s Name: '
            }
            answers = prompt(instructor)

            if answers['Instructor']:
                self.query_df = self.__get_professor(
                    df=self.query_df, answers=answers)

            prereqs = prompt({
                'type': 'confirm',
                'message': 'Do you want prerequisites? ',
                'name': 'prereqs',
                'default': False,
            })

        output = prompt({
            'type': 'confirm',
            'message': 'Want to save the query? ',
            'name': 'save',
            'default': False,
        })

        if output['save'] and not self.query_df.empty:
            self.query_df.to_csv('saved_query.csv')
            print(bolden_blue('SUCESSFUL! Query saved >:D'))
        else:
            print(bolden_blue('UNSUCESSFUL! No results :('))

    def __get_crn(self):
        crn = self.answers['CRN']
        for college in self.colleges:
            majors = glob(join(college, '*.csv'))
            for major in majors:
                crn_df = pd.read_csv(major)
                df['CRN'] = crn_df['CRN'].astype(str)
                if crn_df['CRN'].str.contains(crn).any():
                    return crn_df[(crn_df['CRN'] == crn) & (crn_df['No. of Avail. Seats'] != 0)]

    def __get_course_by_subject(self, answers):
        subject = answers['Subject Code']
        regexp_sub = re.compile(f'\/{subject}.csv')
        course_df = pd.DataFrame()
        for college in self.colleges:
            majors = glob(join(college, '*.csv'))
            for major in majors:
                if regexp_sub.search(major):
                    course_df = pd.read_csv(major)
                    if answers['Course No.']:
                        course_df = course_df[course_df['Course No.']
                                              == answers['Course No.']]
        return course_df

    def __get_num_of_credits(self, df, answers):
        credit_df = df.copy(deep=True)
        num_of_credits = answers['Credits']
        if credit_df.empty:
            for college in self.colleges:
                majors = glob(join(college, '*.csv'))
                for major in majors:
                    df = pd.read_csv(major)
                    if credit_df.empty:
                        credit_df = df[df['Credits'].isin(num_of_credits)]
                    else:
                        credit_df = pd.concat(
                            [credit_df, df[df['Credits'].isin(num_of_credits)]])
        else:
            credit_df = df[df['Credits'].isin(num_of_credits)]
        return credit_df

    def __get_professor(self, df, answers):
        prof_df = df.copy(deep=True)
        prof_name = answers['Instructor']
        if prof_df.empty:
            for college in self.colleges:
                majors = glob(join(college, '*.csv'))
                for major in majors:
                    df = pd.read_csv(major)
                    if prof_df.empty:
                        prof_df = df[df['Instructor'].str.contains(answers['Instructor'])]
                    else:
                        prof_df = pd.concat(
                            [prof_df, df[df['Instructor'].str.contains(answers['Instructor'])]])
        else:
            prof_df = df[df['Instructor'].str.contains(answers['Instructor'])]
        return prof_df

    def __get_no_prereqs(self, df, answers):
        pass


if __name__ == '__main__':
    tprint('Better Course Query'.center(shutil.get_terminal_size().columns//2))

    query = TMSQuery()
    print()
    query.start()
