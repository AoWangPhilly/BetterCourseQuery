from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import re
from typing import Dict, List

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

TMS_URL = 'https://termmasterschedule.drexel.edu/'

# Change later about when quarter become available
# Change year 20-21 to current-yr -> the next
def enter_quarter_page(quarter: str) -> str:
    # Make quarter string Titled
    quarter = quarter.lower().title()

    TMS_PAGE = requests.get(TMS_URL)

    # Get Colleges / Subjects page for the quarter
    soup = BeautifulSoup(TMS_PAGE.content, 'html.parser')

    # Always defaults for Antoinette Westphal COMAD
    return TMS_URL + soup.find('a', href=True, text=f'{quarter} Quarter 20-21')['href']


def get_college(quarter: str, college: str) -> str:
    
    colleges_url = enter_quarter_page(quarter)
    colleges_page = requests.get(colleges_url)
    soup = BeautifulSoup(colleges_page.content, 'html.parser')

    college_page_url = soup.find('a', href=True, text=college)['href']
    return TMS_URL + college_page_url

def get_majors(quarter: str, college: str) -> List[str]:
    html_tables = pd.read_html(get_college(quarter, college))
    table_str = html_tables[6].loc[1][0]
    regex_group = re.findall(r'([a-zA-Z\s&-]+\s\(\w+\))', table_str)
    regex_group = [major.strip() for major in regex_group]
    return regex_group

def get_major_courses(quarter: str, college: str, major: str) -> pd.DataFrame:
    college_url = get_college(quarter, college)
    college_page = requests.get(college_url)
    soup = BeautifulSoup(college_page.content, 'html.parser')

    courses_url= TMS_URL + soup.find('a', text=re.compile(major))['href']
    course_page = requests.get(courses_url)

    return pd.read_html(course_page.content)[4]

if __name__ == '__main__':
    c = get_major_courses('FALL', 'Col of Computing & Informatics', 'CS')
    print(c)
