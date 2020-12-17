# !/usr/bin/env python
'''


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

class TMSQuery():
    def __init__(self, answers):
        self.answers = answers
        self.base_folder = join('DREXEL', answers['quarter'])

    def get_professor(self):
        pass

    def get_credit(self):
        pass

    def get_no_prereqs(self):
        pass

    def get_course(self) -> None:
        pd.set_option('display.max_columns', None)

        sub_code, course_no = self.answers['Subject Code & Course No.'].split(
            ' ')

        if self.answers.get('Subject Code & Course No.', None):
            colleges = glob(join(self.base_folder, '*/'))

        for college in colleges:
            majors = glob(join(college, '*.csv'))
            for major in majors:
                df = pd.read_csv(major)
                df[['Subject Code', 'Course No.']] = df[[
                    'Subject Code', 'Course No.']].astype(str)
                if df['Subject Code'].str.contains(sub_code).any() and df['Course No.'].str.contains(course_no).any():
                    self.print_results(
                        df[(df['Subject Code'] == sub_code) & (df['Course No.'] == course_no)])
                    return

    def get_crn(self):
        pass

    def print_results(self, df: pd.DataFrame) -> None:
        initial_course = df.iloc[0]
        print('{} {}: {}\nDescription: {}\nPrereq: {}\nRestrictions: {}\nCoreqs: {}\n'.format(
              initial_course['Subject Code'], initial_course['Course No.'], initial_course['Course Title'], textwrap.fill(initial_course['Course Desc.'], 100),
              initial_course['Prerequisites'], initial_course['Restrictions'], initial_course['Corequisites']))
        desired_cols = ['Instr Type', 'Instr Method', 'Sec', 'CRN', 'Days / Time',
                        'Instructor', 'Credits', 'No. of Avail. Seats', 'Section Comments']
        print(tabulate(df[desired_cols], showindex=False, headers='keys', tablefmt='psql'))


if __name__ == '__main__':
    # fall = os.path.join('DREXEL', 'FALL', 'Col of Computing & Informatics', 'CS.csv')
    # df = pd.read_csv(fall);

    # print(df)

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
        }
    ]

    answers = prompt(questions)
    query = TMSQuery(answers=answers)
    query.get_course()
