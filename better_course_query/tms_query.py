# !/usr/bin/env python
'''
file: term_query.py
author: ao wang
date: 12/29/25
brief: Helps students find courses they want by: subject, course number, # of credits, prereqs, or professor
'''
from __future__ import print_function, unicode_literals
import pandas as pd
import numpy as np
import shutil
import re
from os.path import join
from glob import glob
from PyInquirer import prompt, print_json, Separator
from tabulate import tabulate
from textwrap import indent
from art import tprint
import sys
import textwrap
from termcolor import colored, cprint


class TMSQuery():
    '''The TMSQuery class helps students find the classes they need better than the TMS search site

    :param query_df: the output dataframe from the search
    :type query_df: pd.DataFrame
    :param answers: answers for which quarter and crn number the course has
    :type answers: dictionary of questions and answers
    :param colleges: list of all the college directories
    :type colleges: list of str
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

    def start(self) -> None:
        '''Begins the query for the user, searches for CRN (unique course id), if there isn't one
        then ask for subject, then course number. Then filter by number of credits, instructor, and 
        if the course has no prerequisites. After the query, there will be a table output; the user can 
        also learn more about a course by selecting its CRN number, providing additional info, like prereqs,
        course name, description, etc. In the end, the user will also have the chance to save the query,
        as a CSV file.
        '''
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
                'message': 'No prerequisites? ',
                'name': 'prereqs',
                'default': False,
            })

            if prereqs['prereqs']:
                self.query_df = self.__get_no_prereqs(
                    df=self.query_df, answers=prereqs)
        self.print_df()

        course_info = [
            {
                'type': 'confirm',
                'message': 'Learn about a course? ',
                'name': 'course?',
                'default': False,
            },
            {
                'type': 'input',
                'message': 'Enter CRN No.: ',
                'name': 'CRN',
                'when': lambda course_info: course_info['course?'] == True
            },
        ]

        answers = prompt(course_info)
        if answers['course?']:
            self.get_course_info(answers)

        output = prompt({
            'type': 'confirm',
            'message': 'Want to save the query? ',
            'name': 'save',
            'default': False,
        })

        if output['save'] and not self.query_df.empty:
            self.query_df.to_csv('saved_query.csv')
            cprint('SUCESSFUL! Query saved >:D', 'green',
                   attrs=['bold'], file=sys.stdout)
        else:
            cprint('UNSUCESSFUL! No results :(', 'red',
                   attrs=['bold'], file=sys.stderr)

    def __get_crn(self) -> pd.DataFrame:
        '''Searches files for courses' CRN number

        :returns: a row of the course with the CRN number
        :rtype: pd.DataFrame
        '''
        crn = self.answers['CRN']
        for college in self.colleges:
            majors = glob(join(college, '*.csv'))
            for major in majors:
                crn_df = pd.read_csv(major)
                df['CRN'] = crn_df['CRN'].astype(str)
                if crn_df['CRN'].str.contains(crn).any():
                    return crn_df[(crn_df['CRN'] == crn) & (crn_df['No. of Avail. Seats'] != 0)]

    def __get_course_by_subject(self, answers) -> pd.DataFrame:
        '''Searches file for courses by subject code and optionally course number

        :param answers:
        :type answers:
        :returns: 
        :rtype: pd.DataFrame
        '''
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

    def __get_num_of_credits(self, df, answers) -> pd.DataFrame:
        '''

        :param df:
        :type df:
        :param answers:
        :type answers:
        :returns:
        :rtype:
        '''
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

    def __get_professor(self, df, answers) -> pd.DataFrame:
        '''


        :param df:
        :type df:
        :param answers:
        :type answers:
        :returns:
        :rtype:
        '''
        prof_df = df.copy(deep=True)
        prof_name = answers['Instructor']
        if prof_df.empty:
            for college in self.colleges:
                majors = glob(join(college, '*.csv'))
                for major in majors:
                    df = pd.read_csv(major)
                    if prof_df.empty:
                        prof_df = df[df['Instructor'].str.contains(
                            answers['Instructor'])]
                    else:
                        prof_df = pd.concat(
                            [prof_df, df[df['Instructor'].str.contains(answers['Instructor'])]])
        else:
            prof_df = df[df['Instructor'].str.contains(answers['Instructor'])]
        return prof_df

    def __get_no_prereqs(self, df, answers) -> pd.DataFrame:
        '''


        :param df:
        :type df:
        :param answers:
        :type answers:
        :returns:
        :rtype:
        '''
        no_prereqs = df.copy(deep=True)
        if no_prereqs.empty:
            for college in self.colleges:
                majors = glob(join(college, '*.csv'))
                for major in majors:
                    df = pd.read_csv(major)
                    if no_prereqs.empty:
                        no_prereqs = df[df['Prerequisites'].isna()]
                    else:
                        no_prereqs = pd.concat(
                            [no_prereqs, df[df['Prerequisites'].isna()]])
        else:
            no_prereqs = df[df['Prerequisites'].isna()]
        return no_prereqs

    def print_df(self) -> None:
        '''

        '''
        # Print out tables
        # Number of rows
        self.query_df.rename(
            columns={'No. of Avail. Seats': 'No. of Seats'}, inplace=True)
        self.query_df = self.query_df[self.query_df['No. of Seats'] != 0]
        self.query_df[['Subject Code', 'Course No.']] = self.query_df[[
            'Subject Code', 'Course No.']].astype(str)
        self.query_df['Course'] = self.query_df['Subject Code'] + \
            " " + self.query_df['Course No.']
        desired_cols = ['Course', 'Instr Type', 'Instr Method',
                        'Sec', 'CRN', 'Days / Time', 'Instructor', 'Credits', 'No. of Seats']
        print()
        print(tabulate(self.query_df[desired_cols], showindex=False,
                       headers='keys', tablefmt='fancy_grid'))

    def get_course_info(self, answers) -> None:
        def indent_text(text, amount): return '\n' + indent(text, amount * ' ')
        if self.query_df.empty:
            cprint('UNSUCESSFUL! Empty dataframe :(',
                   'red', attrs=['bold'], file=sys.stderr)

        self.query_df['CRN'] = self.query_df['CRN'].astype(str)
        has_course = self.query_df[self.query_df['CRN'] ==
                                   answers['CRN']].iloc[0].replace({np.nan: 'None'})
        if has_course.empty:
            cprint('UNSUCESSFUL! No matching for CRN :(',
                   'red', attrs=['bold'], file=sys.stderr)
        else:
            cprint('SUCESSFUL! Found course! >:D', 'green',
                   attrs=['bold'], file=sys.stderr)

            course_title = colored('Course Title:', 'blue', attrs=['bold', 'underline'])
            course = indent_text(
                f"{has_course['Course']} - {has_course['Course Title']}", 4)

            desc_title = colored('Description:', 'blue', attrs=['bold', 'underline'])
            desc = indent_text(
                f"{textwrap.fill(has_course['Course Desc.'], width=100)}", 4)

            prereq_title = colored('Prerequisites:', 'blue', attrs=['bold', 'underline'])
            prereq = indent_text(f"{has_course['Prerequisites']}", 4)

            restrict_title = colored('Restrictions:', 'blue', attrs=['bold', 'underline'])
            restrict = indent_text(f"{has_course['Restrictions']}", 4)

            coreq_title = colored('Corequisites:', 'blue', attrs=['bold', 'underline'])
            coreq = indent_text(f"{has_course['Corequisites']}", 4)

            section_comm_title = colored('Comments:', 'blue', attrs=['bold', 'underline'])
            section_comments = indent_text(f"{has_course['Section Comments']}", 4)

            print(f'{course_title}{course}\n')
            print(f'{desc_title}{desc}\n')
            print(f'{prereq_title}{prereq}\n')
            print(f'{restrict_title}{restrict}\n')
            print(f'{coreq_title}{coreq}\n')
            print(f'{section_comm_title}{section_comments}\n')


if __name__ == '__main__':
    tprint('Better Course Query'.center(shutil.get_terminal_size().columns//2))
    query = TMSQuery()
    print()
    query.start()
