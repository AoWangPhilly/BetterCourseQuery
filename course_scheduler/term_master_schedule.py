#!/usr/bin/env python
'''
file: term_master_schedule.py
author: ao wang
date: 12/12/25
brief: the TMS class web scrapes data for each course and outputs its own flat-file database
'''

from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import re
from typing import Dict, List
import pprint
import os
from pathlib import Path
import multiprocessing


class TMS():
    '''
    TMS class finds URL's for the quarter's and college's pages and finds the table of courses for each colleges.

    Attributes
    ----------
    quarter : str
        quarter system: Fall, Winter, Spring, Summer
    college : str
        Drexel's many colleges, i.e. Col of Computing and Informatics

    Methods
    -------


    '''
    URL = 'https://termmasterschedule.drexel.edu/'

    def __init__(self, quarter: str = None, college: str = None) -> None:
        if quarter:
            quarter = quarter.lower().title()
        self.quarter = quarter
        self.college = college

    def set_quarter(self, quarter: str) -> None:
        if quarter:
            quarter = quarter.lower().title()
        self.quarter = quarter

    def get_quarter(self) -> str:
        return self.quarter

    def set_college(self, college: str) -> None:
        self.college = college

    def get_college(self) -> str:
        return self.college

    # Change later about when quarter become available
    # Change year 20-21 to current-yr -> the next
    def get_quarter_url(self) -> str:
        '''

        '''
        # Make quarter string Titled
        TMS_PAGE = requests.get(TMS.URL)

        # Get Colleges / Subjects page for the quarter
        soup = BeautifulSoup(TMS_PAGE.content, 'html.parser')
        # Always defaults for Antoinette Westphal COMAD
        return TMS.URL + soup.find('a', href=True, text=f'{self.get_quarter()} Quarter 20-21')['href']

    def get_available_college(self):
        '''

        '''
        colleges_url = self.get_quarter_url()
        colleges_page = requests.get(colleges_url)
        soup = BeautifulSoup(colleges_page.content, 'html.parser')
        left_col = soup.find('div', {'id': 'sideLeft'}).findAll('a')
        available_colleges = [c.text for c in left_col]
        return available_colleges

    def get_college_url(self) -> str:
        '''

        '''
        colleges_url = self.get_quarter_url()
        colleges_page = requests.get(colleges_url)
        soup = BeautifulSoup(colleges_page.content, 'html.parser')

        college_page_url = soup.find('a', href=True, text=self.college)['href']

        return TMS.URL + college_page_url

    def get_majors(self) -> List[str]:
        '''

        '''
        college_url = self.get_college_url()
        html_tables = pd.read_html(college_url)
        table_str = html_tables[6].loc[1][0]
        regex_group = re.findall(r'([a-zA-Z\s&-]+\s\(\w+\))', table_str)
        regex_group = [major.strip() for major in regex_group]
        regex_group = [major[major.find(
            '(') + 1: (len(major) - 1)].strip() for major in regex_group]
        return regex_group

    def create_major_to_college_map(self) -> Dict[str, List[str]]:
        '''

        '''
        tms, mapping = TMS(quarter=self.quarter), {}
        colleges = self.get_available_college()
        for college in colleges:
            tms.set_college(college)
            mapping[college] = tms.get_majors()

        return mapping

    def get_major_info(self, crn: str, soup):
        '''

        '''

        crn_url = TMS.URL + soup.find('a', text=crn)['href']
        crn_page = requests.get(crn_url)
        crn_soup = BeautifulSoup(crn_page.content, 'html.parser')

        creds = crn_soup.find('td', attrs={
                              'class': 'tableHeader'}, text='Credits').next_sibling.next_sibling.text.strip()

        enroll = crn_soup.find('td', attrs={
                               'class': 'tableHeader'}, text='Enroll').next_sibling.next_sibling.text.strip()
        available_seats = 0
        if enroll != 'CLOSED':
            max_enroll = crn_soup.find('td', attrs={
                                       'class': 'tableHeader'}, text='Max Enroll').next_sibling.next_sibling.text.strip()
            available_seats = int(max_enroll) - int(enroll)
        section_comments = crn_soup.find('td', attrs={
                                         'class': 'tableHeader'}, text='Section Comments').next_sibling.next_sibling.text.strip().replace('\n\n', '\n')
        course_desc = crn_soup.find('div', attrs={'class': 'courseDesc'}).text

        div = crn_soup.findAll(
            'div', attrs={'class': ['subpoint1', 'subpoint2']})
        restrict = '\n'.join(
            [subpoint.text for subpoint in div if subpoint.text])

        table = crn_soup.find('table', attrs={'class': 'descPanel'})
        spans = table.findAll('span')
        prereqs = ' '.join([span.text.strip()
                            for span in spans if span.text.find('EXAM') == -1])

        co_req = None
        has_b_tag = crn_soup.find(
            'b', text='Co-Requisites:').next_sibling.next_sibling
        if has_b_tag:
            co_req = has_b_tag.text

        return {'Credits': creds, 'No. of Avail. Seats': available_seats, 'Section Comments': section_comments,
                'Course Desc.': course_desc, 'Restrictions': restrict, 'Prerequisites': prereqs, 'Corequisites': co_req}


    def get_major_courses(self, major: str) -> pd.DataFrame:
        '''


        '''
        college_url = self.get_college_url()
        college_page = requests.get(college_url)
        soup = BeautifulSoup(college_page.content, 'html.parser')

        courses_url = TMS.URL + soup.find('a', text=re.compile(f'\({major}\)'))['href']
        course_page = requests.get(courses_url)
        majors_df = pd.read_html(course_page.content)[4]

        majors_df.columns = majors_df.loc[0]
        majors_df.drop([0, len(majors_df)-1], inplace=True)
        majors_df.reset_index(drop=True, inplace=True)

        soup = BeautifulSoup(course_page.content, 'html.parser')

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
                Path(folder).mkdir(parents=True, exist_ok=True)
                tms.get_major_courses(m).to_csv(
                    os.path.join(folder, m+'.csv'), index=False)
