import re
import configparser
import threading
import time
import fuzzywuzzy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions


temp_file = None
parsed_file = None
driver = webdriver
config = configparser.ConfigParser()
component_data = {}
component_names = ['White Blood Cell Count',
'Red Blood Cell Count',
'Hemoglobin',
'Hematocrit',
'Mean Corpuscular Volume',
'Mean Corpuscular Hemoglobin',
'Mean Corpuscular Hemoglobin Concentration',
'Platelet Count',
'RED CELL DISTRIBUTION WIDTH CV',
'NRBC Percent',
'NRBC Absolute',
'Segmented Neutrophil Percent',
'Lymphocyte Percent',
'MONOCYTE PERCENT',
'Eosinophils Percent',
'Basophils Percent',
'Immature Granulocytes Percent',
'Neutrophils Absolute',
'Lymphocyte Absolute',
'Monocytes Absolute',
'Eosinophils Absolute',
'Basophils Absolute',
'Immature Granulocytes Absolute',
'Sodium Serum/Plasma',
'Potassium Serum/Plasma',
'Chloride Serum/Plasma',
'Carbon Dioxide',
'Anion Gap',
'Glucose Random Serum/Plasma',
'Blood Urea Nitrogen',
'Creatinine Serum/Plasma',
'eGFR',
'EGFR African American',
'Calcium Serum/Plasma',
'Bilirubin Total',
'Alkaline Phosphatase Total',
'Alaninine Aminotransferase',
'Aspartate Aminotransferase',
'Protein Total Serum/Plasma',
'ALBUMIN',
'Color Urine',
'Appearance Urine',
'Specific Gravity Urine',
'pH Urine',
'Protein Urine',
'Glucose Urine',
'Ketones Urine',
'Bilirubin Urine',
'Blood Urine',
'Nitrite Urine',
'Urobilinogen Urine',
'Leukocyte Esterase Urine',
'Bilirubin, Direct',
'Bilirubin Indirect',
'Prothrombin Time',
'INR',
'Carcinoembryonic Antigen DXI',
'MAGNESIUM SERUM',
'LIPASE PLASMA',
'AMYLASE SERUM',
'Lactate Dehydrogenase',
'URIC ACID SERUM',
'FREE T3',
'T4 Free',
'TSH',
'Fibrinogen',
'Activated Partial Thromboplastin Time',
'GAMMA GLUTAMYLTRANSFERASE',
'Triglycerides',
'CHOLESTEROL']


def main():
    global temp_file
    global config

    config.read('config.ini')
    temp_file = read_file(config.get("paths", "text_file"))

    threading1 = threading.Thread(target=run_program)
    threading1.daemon = True
    threading1.start()

    read_file('datafile')
    greet_user()
    get_user_input()


def run_program():
    while True:
        check_file_for_update()

def greet_user():
    print("Thanks for using Epic To Survey! \n \t -Created by Nick Rizzo- \n")
    print('//////////////////////////////////\n')
    print('Update the text file with new data to begin')


def get_user_input():
    # main program loop
    while True:
        user_input = input()
        handle_user_input(user_input)


def read_file(file_path):
    file = open(file_path)
    file_text = file.readlines()
    return file_text


def parse_file_into_lists(file):
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
    global component_data
    global component_names

    for line in file:
        component = line[0:73]
        component = str(component).strip()

        datum = line[153:]
        datum = str(datum).strip()

        best_ratio_score = 0
        most_likely_component_datum_pair = ('', '')

        for component_name in component_names:
            ratio_score = fuzz.ratio(component_name, component)
            if ratio_score == 100:
                most_likely_component_datum_pair = (component, datum)
                break
            else:
                if ratio_score > best_ratio_score:
                    most_likely_component_datum_pair = (component, datum)

        component_data[most_likely_component_datum_pair[0]] = most_likely_component_datum_pair[1]

    for x in component_data:
        print(x + ' : ' + component_data[x])
# def parse_file_into_lists(file):
#     global parsed_file
#     global component_data
#
#     components = []
#     ref_data = []
#     real_data_1 = []
#     real_data_2 = []
#     parsed_file = [components, ref_data, real_data_1, real_data_2]
#
#     for line in file:
#         component = line[0:73]
#         component = str(component).strip()
#         components.append(component)
#
#         ref_datum = line[73:131]
#         ref_datum = str(ref_datum).strip()
#         ref_data.append(ref_datum)
#
#         real_datum = line[131:153]
#         real_datum = str(real_datum).strip()
#         real_data_1.append(real_datum)
#
#         real_datum = line[153:]
#         real_datum = str(real_datum).strip()
#         real_data_2.append(real_datum)
#
#         print('{} : {}'.format(component, real_data_2))
#         component_data[component] = real_data_2
#
#
#     return parsed_file


def handle_user_input(user_input):
    if user_input == 'quit':
        driver.quit()
        raise SystemExit


def check_file_for_update():
    global config
    global temp_file

    config.read('config.ini')
    file_path = config.get("paths", "text_file")

    if str(temp_file) != str(read_file(file_path)):
        print('Changes to the file have been detected')
        temp_file = read_file(file_path)
        parse_file_into_lists(temp_file)
        fill_survey()
    else:
        #print('No change to the file detected')
        time.sleep(1)


def fill_survey():
    global driver
    global config
    global field_names

    config.read('config.ini')

    try:
        driver = webdriver.Chrome('chromedriver.exe')
        driver.get(config.get('paths', 'survey_url'))
        find_all_data_field_IDs_in_HTML_Source(driver.page_source)
    except FileNotFoundError:
        print("Web driver not found")

    try:
        # answer 1st question
        for i in range(get_config_section_size('elements')):
            elem = driver.find_element_by_id(config.get('elements', str(i)))
            field_datum = field_names[i]
            print(field_datum)

            elem.send_keys(get_datum_for_field(field_datum))

            elem.send_keys(Keys.TAB)


        #elem.submit()
    except selenium.common.exceptions.NoSuchElementException:
        print("Cannot fill survey")


def get_datum_for_field(datum_field_name):
    global component_data
    config.read('config.ini')
    datum_field_value = config.get('lookup', datum_field_name)

    #print(component_data[datum_field_value])
    return component_data[datum_field_value]


def get_config_section_size(section):
    return len(config.items(section))


def find_all_data_field_IDs_in_HTML_Source(page_source):
    IDs = re.findall('<td>(\w+\s*\w*)<\/td>', page_source)
    element_ids = find_corresponding_field_ID(page_source)



def find_corresponding_field_ID(page_source):
    element_blocks = re.findall(r'_ctl0_Content_R_loclabcontainer_loclabcontainer_\d{6}__ctl0__Text', page_source)
    for element_block in element_blocks:
        print(element_block)
    #return re.match(r'(?<={}).*?(?={})'.format(start, end), page_source)
    # <input name="(\w+|\d+|\:)*"
    # id="(\w+|\d+|\:)*"
    # <input name="(\w+|\d+|\:)*" type="text" maxlength="\d+" id="(\w+|\d+|\:)*"
    return element_blocks


def display_configurations():
    file = open("config.ini")
    print()
    for line in file:
        print(line, end='')


def display_datafile():
    file = open("datafile")
    print()
    for line in file:
        print(line, end='')


if __name__=="__main__":
   main()
