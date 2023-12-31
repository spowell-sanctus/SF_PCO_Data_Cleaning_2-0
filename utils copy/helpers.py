import csv
from datetime import datetime
import json
import re
import string

import pandas as pd


def write_response_file(data, filename):
    
    if type(data) is dict:
        with open(filename+'.json', 'a') as f:
            json.dump(data, f)
    
    elif type(data) is json:
        with open(filename+'.json', 'a', encoding='utf-8') as f:
            json.dump(data.json(), f, ensure_ascii=False, indent=4)

    elif type(data) is list:        
                
        with open(filename+'.csv','a') as f:    
            write = csv.writer(f)
            write.writerow(data[0].get_attendee_headers_list())
            for a in data:
                write.writerow(a.get_attendee_detail_list())


def get_letters_only(word: str):
    # create return variable
    working_word = ''
    # loop through letters in the given string
    for letter in word:
        # if letter a letter
        if letter in string.ascii_letters:
            # concatenate to end of return variable
            working_word += letter
           
    return working_word


def get_valid_email(email):
    
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.match(pattern,email):
        return email
    else:
        # print(f"email: {email} so placeholder email used!\n")
        return 'placeholder@sanctuschurch.com'
    

def get_first_of_multiple(data: str):
    result = data
    # if personal email present
    if data != '':
        # if multiple personal emails
        if ';' in data:
            # only use the first      
            result = data.split(';')[0]
        # assign email to cleaned personal email
    return result


'''Creates a cleaned PCO data file with a new column at the beginning for the unique special ID of firstname+lastname+email'''
def create_special_id(fname: str, lname: str, p_email: str, b_email: str, oth_email: str):

    # set defaults
    sp_fname = get_letters_only(fname)
    sp_lname = get_letters_only(lname)
    email = ''

    # get first of multiple email in each category if multiples exist
    p_email =  get_first_of_multiple(p_email)
    b_email =  get_first_of_multiple(b_email)
    oth_email =  get_first_of_multiple(oth_email)

    # set the default email value to the personal email value 
    email = p_email
    # if p_email is empty but b or oth isn't, use them in that order
    if p_email == '' and b_email != '':
        email = b_email
    elif p_email == '' and oth_email != '':
        email = oth_email
    
    # make sure that the email gotten is valid, or returns placeholder@sanctuschurch.com
    sp_email = get_valid_email(email)

    # clean up the special characters
    
    # if no first name given, set stand-in variable
    if fname == '':
        sp_fname = 'noFirstName'
    # if no last name given, set stand-in variable
    elif lname == '':
        sp_lname = 'noLastName'
         
    # return the special id         
    return sp_fname+sp_lname+sp_email


def convert_numbers_to_boolean(data):
    if(data == '0'):
        return 'False'
    elif(data == '1'):
        return 'True'


def convert_pco_grades(grade: int):
    result = ''
    if grade == -1:
        result = 'Preschool'
    elif grade == 0:
        result = 'Kindergarten'
    elif grade > 0 and grade <= 12:
        result = 'Grade '+ str(grade)
    return result


def get_single_CT_email(email_field):
    email = email_field.strip()
    email = email.split(';',1)[0]
    email = email.replace(' ', '')
    email = get_valid_email(email)
    return email


def get_now(message: str):
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print(f"{message}: {current_time}\n")
    return now


def runtime(start:datetime, end:datetime):
    delta = end - start
    print(f'Runtime: {delta}')
    
def remove_unneeded_columns(incoming_file, drop_sheet, reduced_file):
    columns_to_drop = []    
    drop_data = pd.read_csv(drop_sheet)
    csv_size = len(drop_data)
    # print(f'csv_size: {csv_size}')
    
    with open(drop_sheet,'r',encoding = 'ISO-8859-1') as drop_cols:  
        # print(drop_cols)
        for index, row in enumerate(csv.reader(drop_cols)): 
            if 0 < index <= csv_size:
                # print(f'col: {index} data: {row[0]}')
                columns_to_drop.append(row[0])    
    
    data = pd.read_csv(incoming_file,encoding='latin-1')
    
    for index, col in enumerate(columns_to_drop):
        # print(index)
        # print(f'col: {col}')
        data.drop(col, inplace=True, axis=1)
        
    # print(data)
    data.to_csv(reduced_file, index=False)
    
    
def get_string_note_date(raw_date:str):
    raw_date = datetime.strptime(raw_date,'%Y-%m-%d %H:%M')
    create_day = raw_date.day
    create_month = raw_date.month_name[raw_date.month]
    create_year = raw_date.year
    
    s_date = str(create_day) + " " + str(create_month) + " " + str(create_year)
    print(f'string date: {s_date}')
    return s_date


