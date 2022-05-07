import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

def job_title_search(indeed_job):
    """Function to fetch the job tile from html and label if it is a new job (Y/N)
    returns: job_title (string) and job_new (string)"""
    try:
        job_title = indeed_job.find('h2', class_='jobTitle jobTitle-color-purple')
        job_title.text
        job_new = 'N'
    except AttributeError:
        job_title = indeed_job.find('h2', class_='jobTitle jobTitle-color-purple jobTitle-newJob').find_all('span')[1]
        job_new = 'Y'

    return job_title, job_new


def job_salary_search(indeed_job):
    try:
        job_salary = indeed_job.find('div', class_='attribute_snippet')
        if job_salary.text == 'Full-time':
            job_salary = indeed_job.find('div', class_= 'metadata salary-snippet-container')
    except:
        job_salary = indeed_job.find('span', class_='estimated-salary')
    try:
        job_salary = job_salary.text
    except AttributeError:
        job_salary = 'n/a'

    return job_salary


def company_link_search(item):
    """Function to return the link to the company overview via indeed
    should start with 'https://www.indeed.com/'"""
    c_link = item.find('a', class_="turnstileLink companyOverviewLink")
    try:
        company_link = c_link.get('href')
    except AttributeError:
        company_link = 'n/a'

    return company_link



def job_link_search(item):
    """Function to look for the link which is in a parent <a to the rest of the information"""
    job_link = item.get('href')
    removed_clk = job_link.split('?')[1]
    full_link = 'https://www.indeed.com/viewjob?'+removed_clk

    return full_link


def job_info_search(item):
    """
    Function that will get all the items from a single job posting and input them into a dictionary
    returns job_dic (dictionary)
    """
    job_dic = {}

    indeed_job = item.find('div', class_='job_seen_beacon')

    job_title, job_new = job_title_search(item)
    job_dic['job_title'] = job_title.text
    job_dic['job_new'] = job_new

    job_company = indeed_job.find('span', class_='companyName')
    job_dic['company'] = job_company.text

    company_link = company_link_search(item)
    job_dic['company_link'] = company_link

    job_location = indeed_job.find('div', class_='companyLocation')
    job_dic['location'] = job_location.text

    job_post_date = indeed_job.find('span', class_='date')
    job_dic['posted_date'] = job_post_date.text

    job_salary = job_salary_search(indeed_job)
    job_dic['salary'] = job_salary

    return job_dic


def job_search_dictionary(url):
    """Function to search for Data Scientist jobs in Massachusetts
    returns: my_job_dic (dict)"""

    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    whole_job_page = soup.find_all('a', target='_blank', rel='nofollow')
    my_job_dic = []
    for item in whole_job_page:
        my_job_dic.append(job_info_search(item))

    return my_job_dic


def itterate_through_pages(url):
    """Function to page through the listins by 10 posts"""
    endings = ['','&start=10', '&start=20', '&start=30', '&start=40']
    my_job_dfs = []
    for ends in endings:
        url_endings = url+ ends
        my_job_dic = job_search_dictionary(url_endings)
        my_job_df = pd.DataFrame(my_job_dic)
        my_job_dfs.append(my_job_df)
    final = pd.concat(my_job_dfs)

    return final


def make_clickable(val):
    return f'<a target=_blank" href="{val}">{val}</a>'


def style_results(df):
    return df.style\
.hide_index()\
.format({'company_link': make_clickable})


def complete_company_link(results):
    """function that takes in the final dataframe and converts the company link to a full http clickable link"""
    for i in range(0,len(results['company_link'])):
        if results['company_link'][i] == 'n/a':
            pass
        else:
            results['company_link'][i] = 'https://www.indeed.com' + results['company_link'][i]

    final = style_results(results)

    return final


def indeed_job_search(occupation = 'Data Scientist', location = 'Massachusetts', posting_age = '3'):
    """
    args: occupation (string), location (string), posting_age (string)"""
    occupation_formatted = occupation.replace(' ', '%20')
    full_url = 'https://www.indeed.com/jobs?q=' + occupation_formatted + '&l=' + location + '&fromage='+ posting_age

    my_job_dict = itterate_through_pages(url)
    res = pd.DataFrame(my_job_dict)
    results = res.reset_index(drop=True)
    final = complete_company_link(results)

    display(final)
