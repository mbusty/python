from re import T
import requests
from bs4 import BeautifulSoup
import pprint

def writer(fields_dict):
    #used to write as the script scrapes, in case of loss of connection midway
    print()

def get_sub_fields():
    fields_dict = get_main_fields()
    for field in fields_dict:
        url = fields_dict[field]['href']
        page = requests.get(url)

        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find('table').findAll('tr')
        i = 0
        fields_dict[field]['sub_fields'] = {}
        print(f'Fetching sub fields for {field}')
        for row in table:
            if row.findChild().name == 'td':
                fields_dict[field]['sub_fields'][i] = {}
                for value in range(len(row.findAll('td'))):
                    if value == 0:
                        fields_dict[field]['sub_fields'][i]['field_name'] = row.findAll('td')[value].text
                    elif value == 1:
                        fields_dict[field]['sub_fields'][i]['description'] = row.findAll('td')[value].text
                    elif value == 2:
                        fields_dict[field]['sub_fields'][i]['type'] = row.findAll('td')[value].text
                    elif value == 3:
                        fields_dict[field]['sub_fields'][i]['versions'] = row.findAll('td')[value].text
                i+=1
        tester(fields_dict[field])
    pprint.pprint(fields_dict)


def get_main_fields():
    url = 'https://www.wireshark.org/docs/dfref/'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    fields_dict = {}
    for data in soup.findAll('div', {'class': 'dfref-entry'}):

        # Sanitizing data
        field = data.get_text().split("(")[0].strip()
        field_name = field.split(":")[0]
        field_desc = field.split(":")[1].strip()
        field_href = data.find('a').get('href')

        # Adding data to nested dictionary
        fields_dict[field_name] = {}
        fields_dict[field_name]['description'] = field_desc
        fields_dict[field_name]['href'] = ''.join([url, field_href])

    return fields_dict


def tester(val):
    pprint.pprint(val)


def main():
    # Parses home page and returns dictionary of information
    get_sub_fields()
    # tester()


if __name__ == '__main__':
    main()


    # fields_dict = {
    #     0:
    #     [{
    #         "Field Name": 'abc',
    #         "Description": 'def',
    #         "Type": 'ghi',
    #         "Versions": "jlk"
    #     }]
    # }
