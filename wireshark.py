import requests
from bs4 import BeautifulSoup
import lxml
import cchardet
import pprint
import sys
import os
import getopt
import json
from tqdm import tqdm


def get_fields():
    try:
        # Fetching wireshark's webpage for scraping
        url = 'https://www.wireshark.org/docs/dfref/'
        requests_session = requests.Session()
        page = requests_session.get(url)

        soup = BeautifulSoup(page.content, 'lxml')

        fields_dict = {}
        for data in tqdm(soup.findAll('div', {'class': 'dfref-entry'}), total=len(list(soup.findAll('div', {'class': 'dfref-entry'}))), desc='Fetching Fieldnames'):

            # Sanitizing data
            field = data.get_text().split("(")[0].strip()
            field_name = field.split(":")[0]
            field_desc = field.split(":")[1].strip()
            field_href = data.find('a').get('href')

            # Adding data to nested dictionary
            fields_dict[field_name] = {}
            fields_dict[field_name]['description'] = field_desc
            fields_dict[field_name]['href'] = ''.join([url, field_href])

            # Fetching sub webpages from wireshark's main page
            sub_url = fields_dict[field_name]['href']
            sub_page = requests_session.get(sub_url)

            sub_soup = BeautifulSoup(sub_page.content, 'lxml')
            table = sub_soup.find('table').findAll('tr')
            i = 0
            fields_dict[field_name]['sub_fields'] = {}
            for row in table:
                if row.findChild().name == 'td':
                    fields_dict[field_name]['sub_fields'][i] = {}
                    # Organizing tables to be appended to the nested dictionary
                    for value in range(len(row.findAll('td'))):
                        if value == 0:
                            fields_dict[field_name]['sub_fields'][i]['field_name'] = row.findAll('td')[value].text
                        elif value == 1:
                            fields_dict[field_name]['sub_fields'][i]['description'] = row.findAll('td')[value].text
                        elif value == 2:
                            fields_dict[field_name]['sub_fields'][i]['type'] = row.findAll('td')[value].text
                        elif value == 3:
                            fields_dict[field_name]['sub_fields'][i]['versions'] = row.findAll('td')[value].text
                i+=1
    except:
        print('An error has occured while fetching the fieldnames, only a portion will be written to the output file')
    finally:
        return fields_dict

def writer(file):
    if file.endswith('.json'):
        with open(file, 'w+') as json_file:
            data = get_fields()
            print(f'Writing Fieldnames to {file}')
            json.dump(data, json_file)
            print('Done')
    elif file.endswith('.csv'):
        print(file, 'writing to csv file')


def main(argv):
    options = 'ho:'
    help_prompt = """
Usage: [wireshark_scraper.py] [-o filename]
Scrapes wireshark documentation for fieldname information in order to support data normalization on the Big Data Platform.

Arguements:
    -h: Prints this help prompt.
    -o: Output File (.json or .csv only)   
    """
    if len(argv) < 1:
        print('No arguements found')
        print(help_prompt)
    try:
        arguments, values = getopt.getopt(argv, options)
        for current_arg, current_val in arguments:
            if current_arg in ('-h'):
                print(help_prompt)
            elif current_arg in ('-o'):
                if current_val.endswith('.json') or current_val.endswith('.csv'):
                    writer(current_val) 
                else:    
                    print('Only files ending in .json or .csv are supported at this time')
    except getopt.GetoptError as err:
        print(str(err))
        print(help_prompt)


if __name__ == '__main__':
    main(sys.argv[1:])
