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


class color:
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
    return color.BOLD + color.BLUE + color.UNDERLINE + title + color.END


def indent(text, amount, ch=' '):
    return "\n" + textwrap.indent(text, amount * ch)


class TMSQuery():
    def __init__(self, answers):
        self.answers = answers
        self.base_folder = join('DREXEL', answers['quarter'])

    # @TODO maybe format output different by PROF
    def get_professor(self):
        prof = self.answers['Professor']
        colleges = glob(join(self.base_folder, '*/'))
        for college in colleges:
            majors = glob(join(college, '*.csv'))
            for major in majors:
                df = pd.read_csv(major)
                if df['Instructor'].str.contains(prof).any():
                    found_prof = df[df['Instructor'].str.contains(r'\b' + prof + r'\b', regex=True)]
                    self.print_results(found_prof)

    # @TODO maybe format output different by credits
    def get_credit(self):
        cred = self.answers['Credits']
        colleges = glob(join(self.base_folder, '*/'))
        for college in colleges:
            majors = glob(join(college, '*.csv'))
            for major in majors:
                df = pd.read_csv(major)
                df['Credits'] = df['Credits'].astype(str)
                if df['Credits'].str.contains(cred).any():
                    self.print_results(df[df['Credits'] == cred])

    def get_no_prereqs(self):
        pass

    def get_course(self) -> None:
        pd.set_option('display.max_columns', None)

        sub_code, course_no = self.answers['Subject Code & Course No.'].split(
            ' ')
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
        crn = self.answers['CRN']
        colleges = glob(join(self.base_folder, '*/'))
        for college in colleges:
            majors = glob(join(college, '*.csv'))
            for major in majors:
                df = pd.read_csv(major)
                df['CRN'] = df['CRN'].astype(str)
                if df['CRN'].str.contains(crn).any():
                    self.print_results(df[df['CRN'] == crn])
                    return

    def print_results(self, df: pd.DataFrame) -> None:
        if len(df) == 0: return
        initial_course = df.iloc[0].replace({np.nan: 'None'})
        title = indent(
            f"{initial_course['Subject Code']} {initial_course['Course No.']} - {initial_course['Course Title']}", 4)
        desc = indent(textwrap.fill(
            initial_course['Course Desc.'], width=100), 4)
        prereq = indent(initial_course['Prerequisites'], 4)
        restrict = indent(initial_course['Restrictions'], 4)
        coreq = indent(initial_course['Corequisites'], 4)
        print(f"{bolden_blue('Course Title:')}{title}\n\n{bolden_blue('Description:')}{desc}\n\n{bolden_blue('Prerequisites:')}{prereq}\n\n{bolden_blue('Restrictions:')}{restrict}\n\n{bolden_blue('Corequisites:')}{coreq}\n")

        desired_cols = ['Instr Type', 'Instr Method', 'Sec', 'CRN', 'Days / Time',
                        'Instructor', 'Credits', 'No. of Avail. Seats', 'Section Comments']
        print(tabulate(df[desired_cols], showindex=False,
                       headers='keys', tablefmt='fancy_grid'))


if __name__ == '__main__':
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
            'name': 'CRN',
            'message': 'Enter Course CRN #',
            'when': lambda answers: answers['find_by'] == 'CRN #'
        },
        {
            'type': 'input',
            'name': 'Credits',
            'message': 'Enter # of Credits',
            'when': lambda answers: answers['find_by'] == 'No. of Credits'
        },
        {
            'type': 'input',
            'name': 'Professor',
            'message': 'Enter Professor\'s Name',
            'when': lambda answers: answers['find_by'] == 'Professor'
        }
    ]

    answers = prompt(questions)
    query = TMSQuery(answers=answers)
    print()
    if 'Subject Code & Course No.' in answers:
        query.get_course()
    elif 'CRN' in answers:
        query.get_crn()
    elif 'Credits' in answers:
        query.get_credit()
    elif 'Professor' in answers:
        query.get_professor()

    # print(bolden_blue('Course Name:') + indent('CS 265 - Advanced Programming Tools and Techniques', 5))
