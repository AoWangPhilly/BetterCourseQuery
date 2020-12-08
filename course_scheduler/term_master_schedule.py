from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import re

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
# Change later about when quarter become available
# Change year 20-21 to current-yr -> the next


def enter_quarter_page(quarter: str) -> str:
    # Make quarter string Titled
    quarter = quarter.lower().title()

    TMS_URL = 'https://termmasterschedule.drexel.edu/'
    TMS_PAGE = requests.get(TMS_URL)

    # Get Colleges / Subjects page for the quarter
    soup = BeautifulSoup(TMS_PAGE.content, 'html.parser')

    # Always defaults for Antoinette Westphal COMAD
    return TMS_URL + soup.find('a', href=True, text=f'{quarter} Quarter 20-21')['href']


def get_majors(quarter: str):
    colleges_url = enter_quarter_page('FALL')
    colleges_page = requests.get(colleges_url)
    html_tables = pd.read_html(colleges_page.content)
    table_str = html_tables[6].loc[1][0]
    regex_str = re.findall(r'([a-zA-Z\s&-]+\s\(\w+\))', table_str)
    print(regex_str)


if __name__ == '__main__':
    colleges_url = enter_quarter_page('FALL')
    colleges_page = requests.get(colleges_url)
    html_tables = pd.read_html(colleges_page.content)
    table_str = html_tables[0]
    print(table_str)
