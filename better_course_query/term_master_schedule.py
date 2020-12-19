#!/usr/bin/env python
'''
file: term_master_schedule.py
author: ao wang
date: 12/12/25
brief: the TMS class web scrapes data for each course and outputs its own flat-file database
'''

import bs4
import requests
import re
import pandas as pd
import datetime
import pprint
import os
import multiprocessing
from bs4 import BeautifulSoup
from typing import Dict, List
from pathlib import Path


class TMS():
    '''
    TMS class finds URL's for the quarter's and college's pages and finds the table of courses for each colleges.

    :param quarter: quarter system -> Fall, Winter, Spring, Summer
    :type quarter: str
    :param college: Drexel's many colleges, i.e. Col of Computing and Informatics
    :type college: str
    '''

    # BASE URL
    URL = 'https://termmasterschedule.drexel.edu/'

    def __init__(self, quarter: str = None, college: str = None) -> None:
        '''Constructor method'''
        if quarter: quarter = quarter.lower().title()
        self.quarter = quarter
        self.college = college

    def set_quarter(self, quarter: str) -> None:
        if quarter: quarter = quarter.lower().title()
        self.quarter = quarter

    def get_quarter(self) -> str:
        return self.quarter

    def set_college(self, college: str) -> None:
        self.college = college

    def get_college(self) -> str:
        return self.college

    def get_quarter_url(self) -> str:
        '''Scrapes quarter URL 
        
        :return: the quarter page URL
        :rtype: str
        '''
        TMS_PAGE = requests.get(TMS.URL)

        # Get Colleges / Subjects page for the quarter
        soup = BeautifulSoup(TMS_PAGE.content, 'html.parser')

        # Always defaults for Antoinette Westphal COMAD
        return TMS.URL + soup.find('a', href=True, text=f'{self.get_quarter()} Quarter 20-21')['href']

    def get_available_college(self) -> List[str]:
        '''Gets the list of available colleges for specific quarter

        :returns: a list of college names
        :rtype: a list of strings
        '''
        quarter_url = self.get_quarter_url()
        quarter_page = requests.get(quarter_url)
        quarter_soup = BeautifulSoup(quarter_page.content, 'html.parser')

        # From the left side column, there's a list of college links
        left_col = quarter_soup.find('div', {'id': 'sideLeft'}).findAll('a')
        available_colleges = [a_tag.text for a_tag in left_col]
        return available_colleges

    def get_college_url(self) -> str:
        '''Gets the college URL that contains the list of majors

        :return: the college URL
        :rtype: str
        '''
        quarter_url = self.get_quarter_url()
        quarter_page = requests.get(quarter_url)
        quarter_soup = BeautifulSoup(quarter_page.content, 'html.parser')

        # Get specific hyperlink for college
        college_page_url = quarter_soup.find('a', href=True, text=self.college)['href']

        return TMS.URL + college_page_url

    def get_majors(self) -> List[str]:
        '''Gets a list of all the majors in a speific college

        :return: a list of majors in a college
        :rtype: a list of strings
        '''
        college_url = self.get_college_url()

        # From HTML code get the string of majors
        html_tables = pd.read_html(college_url)
        table_str = html_tables[6].loc[1][0]

        # Find all the elements that match the regex, strip whitespace, and get only the Subject Code
        regex_group = re.findall(r'([a-zA-Z\s&-]+\s\(\w+\))', table_str)
        regex_group = [major.strip() for major in regex_group]
        regex_group = [major[major.find(
            '(') + 1: (len(major) - 1)].strip() for major in regex_group]
        return regex_group

    def create_major_to_college_map(self) -> Dict[str, List[str]]:
        '''Generate a mapping to assign college name to list of majors

        :return: a dictionary with college key to major list value
        :rtype: dictionary of string keys and list of string values
        '''
        tms, mapping = TMS(quarter=self.quarter), {}
        colleges = self.get_available_college()

        # Loop through college names and assign to list of majors
        for college in colleges:
            tms.set_college(college)
            mapping[college] = tms.get_majors()

        return mapping

    def get_major_info(self, crn: str, soup: bs4.BeautifulSoup):
        '''Gets information (# of creds, prereqs, coreqs, etc.) for each course line item

        :param crn: unique course CRN number
        :type crn: str
        :param soup: BeautifulSoup object of the list of majors page
        :type soup: bs4.BeautifulSoup
        '''

        # CRN page
        crn_url = TMS.URL + soup.find('a', text=crn)['href']
        crn_page = requests.get(crn_url)
        crn_soup = BeautifulSoup(crn_page.content, 'html.parser')   

        # Grab Credits and # of students enrolled in class
        creds = crn_soup.find('td', attrs={
                              'class': 'tableHeader'}, text='Credits').next_sibling.next_sibling.text.strip()

        enroll = crn_soup.find('td', attrs={
                               'class': 'tableHeader'}, text='Enroll').next_sibling.next_sibling.text.strip()

        # Set available to 0 because if enroll is closed, there's 0 seats
        # But if not, then subtract from maximum enroll to get available seats
        available_seats = 0
        if enroll != 'CLOSED':
            max_enroll = crn_soup.find('td', attrs={
                                       'class': 'tableHeader'}, text='Max Enroll').next_sibling.next_sibling.text.strip()
            available_seats = int(max_enroll) - int(enroll)
        
        # Get Section comments, course description
        section_comments = crn_soup.find('td', attrs={
                                         'class': 'tableHeader'}, text='Section Comments').next_sibling.next_sibling.text.strip().replace('\n\n', '\n')
        course_desc = crn_soup.find('div', attrs={'class': 'courseDesc'}).text

        # Get all the restrictions for course line item
        div = crn_soup.findAll(
            'div', attrs={'class': ['subpoint1', 'subpoint2']})
        restrict = '\n'.join(
            [subpoint.text for subpoint in div if subpoint.text])

        # Get the prereqs
        table = crn_soup.find('table', attrs={'class': 'descPanel'})
        spans = table.findAll('span')
        prereqs = ' '.join([span.text.strip()
                            for span in spans if span.text.find('EXAM') == -1])

        # Get Coreqs
        co_req = None
        has_b_tag = crn_soup.find(
            'b', text='Co-Requisites:').next_sibling.next_sibling
        if has_b_tag: co_req = has_b_tag.text

        return {'Credits': creds, 'No. of Avail. Seats': available_seats, 'Section Comments': section_comments,
                'Course Desc.': course_desc, 'Restrictions': restrict, 'Prerequisites': prereqs, 'Corequisites': co_req}


    def get_major_courses(self, major: str) -> pd.DataFrame:
        '''Get dataframe of all the courses in the major

        :param major: the subject code, i.e. MATH, CS, PHYS
        :type major: str
        :returns: a dataframe with all courses for that major
        :rtype: pd.DataFrame
        '''

        # Grab college page
        college_url = self.get_college_url()
        college_page = requests.get(college_url)
        soup = BeautifulSoup(college_page.content, 'html.parser')

        # Grab major page then grab table of majors
        courses_url = TMS.URL + soup.find('a', text=re.compile(f'\({major}\)'))['href']
        course_page = requests.get(courses_url)

        # Make that table of majors into a dataframe
        majors_df = pd.read_html(course_page.content)[4]

        # Clean up dataframe to make first row the column then drop the first row and the last (it's blank)
        majors_df.columns = majors_df.loc[0]
        majors_df.drop([0, len(majors_df)-1], inplace=True)
        majors_df.reset_index(drop=True, inplace=True)

        soup = BeautifulSoup(course_page.content, 'html.parser')

        # Apply the info method to create more columns
        majors_df = majors_df.join(majors_df['CRN'].apply(
            lambda x: pd.Series(self.get_major_info(x, soup))))
        return majors_df


if __name__ == '__main__':
    tms = TMS()
    for q in ['FALL', 'WINTER', 'SPRING', 'SUMMER']:
        tms.set_quarter(q)
        mapping = tms.create_major_to_college_map()
        for c in mapping:
            tms.set_college(c)
            for m in mapping[c]:
                print(f'{q} {c} {m}')
                folder = os.path.join('DREXEL', q, c)
                if not os.path.exists(folder): os.makedirs(folder)
                # Path(folder).mkdir(parents=True, exist_ok=True)
                tms.get_major_courses(m).to_csv(
                    os.path.join(folder, m+'.csv'), index=False)
