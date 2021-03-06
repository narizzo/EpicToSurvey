import re
import configparser
import threading
import time
import fuzzywuzzy
from selenium import webdriver
import selenium.common.exceptions

# file:///C:/Users/Nick/Desktop/FinalMICRF.html

__temp_file__ = None
__parsed_file__ = None
__driver__ = webdriver
__config__ = configparser.RawConfigParser()
__component_data_pairs__ = {}
__uco_input_element_pairs__ =  {'alt': 'alaninine aminotransferase',
                                'albumin': 'albumin',
                                'alkaline phosphatase': 'alkaline phosphatase total',
                                'amylase': 'amylase serum',
                                'ast': 'aspartate aminotransferase',
                                'bilirubin indirect': 'bilirubin indirect',
                                'total bilirubin': 'bilirubin total',
                                'bilirubin direct': 'bilirubin, direct',
                                'blood urea nitrogen (bun)': 'blood urea nitrogen',
                                'calcium': 'calcium serum/plasma',
                                'bicarbonate': 'carbon dioxide',
                                'chloride': 'chloride serum/plasma',
                                'cholesterol': 'cholesterol',
                                'creatinine': 'creatinine serum/plasma',
                                'gamma glutamyl transferase (ggt)': 'gamma glutamyltransferase',
                                'glucose': 'glucose random serum/plasma',
                                'ldh': 'lactate dehydrogenase',
                                'lipase': 'lipase plasma',
                                'magnesium': 'magnesium serum',
                                'potassium': 'potassium serum/plasma',
                                'total protein': 'protein total serum/plasma',
                                'sodium': 'sodium serum/plasma',
                                'triglycerides': 'triglycerides',
                                'uric acid': 'uric acid serum'}
__is_test__ = False


def main():
    global __temp_file__
    global __config__
    global __driver__

    __config__.read('config.ini')
    __temp_file__ = read_file(__config__.get("paths", "text_file"))

    try:
        __driver__ = webdriver.Chrome('chromedriver.exe')
        __driver__.maximize_window()
        if __is_test__:
            __driver__.get('file:///C:/Users/Nick/Desktop/FinalMICRF.html')
        else:
            __driver__.get(__config__.get('paths', 'login_page'))
    except FileNotFoundError:
        print("Web driver not found")


    threading1 = threading.Thread(target=run_program)
    threading1.start()

    threading2 = threading.Thread(target=start_user)
    threading2.start()


def start_user():
    greet_user()
    get_user_input()


def run_program():
    while True:
        check_file_for_update()


def greet_user():
    print("Thanks for using Epic To Survey! \n \t -Created by Nick Rizzo :: nrizzo414@gmail.com- \n")
    print('//////////////////////////////////\n')
    print('> Update the text file with new data to begin')


def get_user_input():
    while True:
        print("> Enter 'quit' to exit the program and close the browser")
        user_input = input()
        handle_user_input(user_input)


def sort_dictionary():
    from collections import OrderedDict
    sortedDict = OrderedDict(sorted(__uco_input_element_pairs__.items()))
    for key in sortedDict:
        print('\'' + __uco_input_element_pairs__[key].lower() + '\'' + ": " + '\'' + key.lower() + '\',')


def read_file(file_path):
    file = open(file_path)
    file_text = file.readlines()
    return file_text


def handle_user_input(user_input):
    if user_input == 'quit':
        __driver__.quit()
        raise SystemExit


def check_file_for_update():
    global __config__
    global __temp_file__

    __config__.read('config.ini')
    file_path = __config__.get("paths", "text_file")

    if str(__temp_file__) != str(read_file(file_path)):
        print('> Changes to the file have been detected')
        __temp_file__ = read_file(file_path)
        find_component_data_pairs_from_text_file(__temp_file__)
        fill_survey()
    else:
        time.sleep(.5)


def fill_survey():
    from selenium.webdriver.support.ui import Select
    global __driver__
    global __config__
    global field_names
    valid_url = ''

    __config__.read('config.ini')

    is_invalid_url = True
    while is_invalid_url:
        if __is_test__:
            valid_url = 'file:///C:/Users/Nick/Desktop/FinalMICRF.html'
        else:
            valid_url = __config__.get('paths', 'survey_url')
            valid_url = valid_url[:len(valid_url)-6]

        if __driver__.current_url == valid_url:
            is_invalid_url = False

            # select U of CO Hospital from drop down
            select = Select(__driver__.find_element_by_id('_ctl0_Content_R_header_LOC_DropDown'))
            select.select_by_value('22')

            # fill fields
            try:
                element_target_pairs = find_element_target_pairs_in_html(__driver__.page_source)
                for each in element_target_pairs:
                    input_field = __driver__.find_element_by_id(element_target_pairs[each])
                    input_field.send_keys(__component_data_pairs__[__uco_input_element_pairs__[each]])

            except selenium.common.exceptions.NoSuchElementException:
                print("> Cannot fill survey")

        else:
            print('> Invalid survey URL')
            time.sleep(.5)


def find_element_target_pairs_in_html(page_source):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    soup_parts = soup.find_all('td', class_=False)
    element_ids = []
    for part in soup_parts:
        element_ids.append(part.text)

    element_ids = remove_false_element_IDs(element_ids)
    input_ids = find_input_field_IDs_in_HTML(page_source)
    element_target_pairs = {}

    for n in range(len(element_ids)):
        element_target_pairs[element_ids[n]] = input_ids[n]

    return element_target_pairs


def remove_false_element_IDs(IDs):
    # currently only works for U of CO data
    new_id_list = []
    for id in IDs:
        if id.lower() in __uco_input_element_pairs__:
            new_id_list.append(id.lower())
    return new_id_list


def find_input_field_IDs_in_HTML(page_source):
    return re.findall(r'_ctl0_Content_R_loclabcontainer_loclabcontainer_\d{6}__ctl0__Text', page_source)


def find_component_data_pairs_from_text_file(file):
    global __component_data_pairs__

    for line in file:
        component = line[0:73]
        component = str(component).strip()

        datum = line[153:]
        datum = str(datum).strip()

        if component.lower() in __uco_input_element_pairs__.values():
            __component_data_pairs__[component.lower()] = datum

    # for each in __component_data_pairs__:
    #     print(each + ' : ' + __component_data_pairs__[each])

        # if component != '' and datum != '':
        #     best_ratio_score = 0
        #     most_likely_component = ''
        #     most_likely_datum = ''
        #
        #     for component_name in component_names:
        #         ratio_score = fuzz.ratio(component_name, component)
        #         if ratio_score == 100:
        #             most_likely_component = component
        #             most_likely_datum = datum
        #             break
        #         else:
        #             if ratio_score > best_ratio_score:
        #                 most_likely_component = component
        #                 most_likely_datum = datum
        #     component_data[most_likely_component] = most_likely_datum


if __name__=="__main__":
   main()