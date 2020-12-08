from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import re
from typing import Dict, List
import pickle
import pprint

class TMS():
    COLLEGES = ['Antoinette Westphal COMAD',
                'Arts and Sciences',
                'Bennett S. LeBow Coll. of Bus.',
                'Center for Civic Engagement',
                'Close Sch of Entrepreneurship',
                'Col of Computing & Informatics',
                'College of Engineering',
                'Dornsife Sch of Public Health',
                'Goodwin Coll of Prof Studies',
                'Graduate College',
                'Miscellaneous',
                'Nursing & Health Professions',
                'Pennoni Honors College',
                'Sch.of Biomed Engr,Sci & Hlth',
                'School of Education']

    URL = 'https://termmasterschedule.drexel.edu/'

    def __init__(self, quarter: str, college: str) -> None:
        self.quarter = quarter.lower().title()
        self.college = college

    def set_quarter(self, quarter: str) -> None:
        self.quarter = quarter
    
    def get_quarter(self) -> str:
        return self.quarter
    
    def set_college(self, college: str) -> None:
        self.college = college
    
    def get_college(self) -> str:
        return self.college

    # Change later about when quarter become available
    # Change year 20-21 to current-yr -> the next
    def get_quarter(self) -> str:
        # Make quarter string Titled
        TMS_PAGE = requests.get(TMS.URL)

        # Get Colleges / Subjects page for the quarter
        soup = BeautifulSoup(TMS_PAGE.content, 'html.parser')

        # Always defaults for Antoinette Westphal COMAD
        return TMS.URL + soup.find('a', href=True, text=f'{self.quarter} Quarter 20-21')['href']


    def get_college(self) -> str:
        colleges_url = self.get_quarter()
        colleges_page = requests.get(colleges_url)
        soup = BeautifulSoup(colleges_page.content, 'html.parser')

        college_page_url = soup.find('a', href=True, text=self.college)['href']
        return TMS.URL + college_page_url

    def get_majors(self) -> List[str]:
        html_tables = pd.read_html(self.get_college())
        table_str = html_tables[6].loc[1][0]
        regex_group = re.findall(r'([a-zA-Z\s&-]+\s\(\w+\))', table_str)
        regex_group = [major.strip() for major in regex_group]
        return regex_group

    def create_major_to_college_map(self) -> Dict[str, List[str]]:
        mapping = {college: TMS(self.quarter, college).get_majors() for college in TMS.COLLEGES}
        with open('college_course_mapping.p', 'wb') as fp:
            pickle.dump(mapping, fp, protocol=pickle.HIGHEST_PROTOCOL)
        return mapping
        
    def get_major_courses(self, major: str) -> pd.DataFrame:
        college_url = self.get_college()
        college_page = requests.get(college_url)
        soup = BeautifulSoup(college_page.content, 'html.parser')

        courses_url= TMS.URL + soup.find('a', text=re.compile(major))['href']
        course_page = requests.get(courses_url)

        return pd.read_html(course_page.content)[4]


if __name__ == '__main__':
    tms = TMS(quarter='FALL', college='Col of Computing & Informatics')
    c = tms.create_major_to_college_map()
    pprint.pprint(c)
