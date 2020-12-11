from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import re
from typing import Dict, List
import pickle
import pprint
import os
from pathlib import Path
import multiprocessing

class TMS():
    URL = 'https://termmasterschedule.drexel.edu/'

    def __init__(self, quarter: str = None, college: str = None) -> None:
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

    # Change later about when quarter become available
    # Change year 20-21 to current-yr -> the next
    def get_quarter_url(self) -> str:
        # Make quarter string Titled
        TMS_PAGE = requests.get(TMS.URL)

        # Get Colleges / Subjects page for the quarter
        soup = BeautifulSoup(TMS_PAGE.content, 'html.parser')
        # Always defaults for Antoinette Westphal COMAD
        return TMS.URL + soup.find('a', href=True, text=f'{self.get_quarter()} Quarter 20-21')['href']

    def get_available_college(self):
        colleges_url = self.get_quarter_url()
        colleges_page = requests.get(colleges_url)
        soup = BeautifulSoup(colleges_page.content, 'html.parser')
        left_col = soup.find('div', {'id': 'sideLeft'}).findAll('a')
        available_colleges = [c.text for c in left_col]
        return available_colleges
    
    def get_college_url(self) -> str:
        colleges_url = self.get_quarter_url()
        colleges_page = requests.get(colleges_url)
        soup = BeautifulSoup(colleges_page.content, 'html.parser')
        
        college_page_url = soup.find('a', href=True, text=self.college)['href']
    
        return TMS.URL + college_page_url

    def get_majors(self) -> List[str]:
        college_url = self.get_college_url()
        html_tables = pd.read_html(college_url)
        table_str = html_tables[6].loc[1][0]
        regex_group = re.findall(r'([a-zA-Z\s&-]+\s\(\w+\))', table_str)
        regex_group = [major.strip() for major in regex_group]
        regex_group = [major[major.find('(') + 1: (len(major) - 1)] for major in regex_group]
        return regex_group

    def create_major_to_college_map(self) -> Dict[str, List[str]]:
        tms, mapping = TMS(quarter=self.quarter), {}
        colleges = self.get_available_college()
        for college in colleges:
            tms.set_college(college)
            mapping[college] = tms.get_majors()
            
#         with open('college_course_mapping.p', 'wb') as fp:
#             pickle.dump(mapping, fp, protocol=pickle.HIGHEST_PROTOCOL)
        return mapping
        
    def get_major_courses(self, major: str) -> pd.DataFrame:
        college_url = self.get_college_url()
        college_page = requests.get(college_url)
        soup = BeautifulSoup(college_page.content, 'html.parser')

        courses_url= TMS.URL + soup.find('a', text=re.compile(major))['href']
        course_page = requests.get(courses_url)
        majors_df = pd.read_html(course_page.content)[4]
        
        majors_df.columns = majors_df.loc[0]
        majors_df.drop([0, len(majors_df)-1], inplace=True)
        majors_df.reset_index(drop=True, inplace=True)
        
        soup = BeautifulSoup(course_page.content, 'html.parser')
        p_titles = soup.findAll('p')
        p_titles = pd.Series([p.get('title') for p in p_titles if p.get('title')])

        def grab_available_seats(row):
            seats_search = re.search(r'Max enroll=(\d+); Enroll=(\d+)', row)
            if seats_search:
                return int(seats_search.group(1)) - int(seats_search.group(2))
            return 0
        
        majors_df['No. of Available Seats'] = p_titles.apply(grab_available_seats)
#         print(grab_available_seats('Max enroll=38; Enroll=32'))
#         print(p_titles)
        return majors_df


if __name__ == '__main__':
    # tms = TMS(quarter='FALL', college='Col of Computing & Informatics')
    # c = tms.get_major_courses('CS')
    # gui = show(c)
    df = pd.DataFrame(([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), columns=['a', 'b', 'c'])
    show(df)
    # with open('college_course_mapping.p', 'rb') as fp:
    #     data = pickle.load(fp)
    #     pprint.pprint(type(data))