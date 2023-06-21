import csv
from datetime import datetime
import re
import string

from utils.helpers import convert_numbers_to_boolean, create_special_id
from utils.helpers import convert_pco_grades
from utils.helpers import get_letters_only
from utils.helpers import get_valid_email


'''Creates a new file that appends a column at the end for Association Label between Contact and Household'''
def add_pco_household_label(import_file,contact_house):    

    # open the export from pco
    with open(import_file,'r',encoding = 'ISO-8859-1') as csvinput:
        # create a file to recieve the updated information
        with open(contact_house, 'w') as csvoutput:
            # create the writer object
            writer = csv.writer(csvoutput)

            for index, row in enumerate(csv.reader(csvinput)):
                have_primary = False 
                if index == 0:
                    writer.writerow(row+['Association Label'])
                else:                    
                    # if pco, grab these cells for the creation of a household object csv
                    have_primary = row[5] + ' ' + row[8] == row[55] 
                    
                    if have_primary:
                        writer.writerow(row+['Primary Household Contact'])
                    elif row[55] != '':
                        writer.writerow(row+['Other Household Member'])
                    else: 
                        writer.writerow(row)
               

'''Creates a new file that hold the records for Households, one per primary contact on the contact data'''
def create_pco_household_csv(import_file, household_file):
    
    # open the export from pco
    with open(import_file,'r',encoding = 'ISO-8859-1') as csvinput:        
        # create a file to recieve the updated information
        with open(household_file, 'w') as csvoutput:
            # create the writer object
            writer_out = csv.writer(csvoutput)
            
            # loop through the data export
            for index, row in enumerate(csv.reader(csvinput)): 
                # if index of input is zero, create row for households csv - bad association!
                if index == 0:
                    first_row = ['Household Name','Street Address', 'City', 'Province/State', 'Postal Code', 'Household Phone'] 
                    # write the header row for households                       
                    writer_out.writerow(first_row)
                else: 
                    # create list to append data for the row taken from the csvinput file
                    household_details = []
                    
                    # if pco, grab these cells for the creation of a household object csv
                    have_primary = row[5] + ' ' + row[8] == row[55]  
                    # if have  primary, write to the households csv
                    # don't write if not primary to avoid duplication of household records                     
                    if have_primary:
                        household_details.append(row[54].strip())
                        household_details.append(row[28].strip())
                        household_details.append(row[30].strip())
                        household_details.append(row[31].strip())
                        household_details.append(row[32].strip())
                        household_details.append(row[43].strip())
                        writer_out.writerow(household_details)


'''Cleans the data from PCO export for import into HubSpot contacts (no associations)'''
def clean_pco_data(row):

    mobile_phone = row[42]
    home_phone = row[43]                
    p_email = row[49]  
    b_email = row[50]
    oth_email = row[51]
    prov = row[30].strip()
    grade = row[12]
    membership = row[18]
    campus_name = row[21]
    primary_site = row [63]
    date_of_baptism = row[91]
    attending_since = row[67]

    # if multiple phone numbers held in mobile phone cell
    if(';' in mobile_phone):
        # keep only the first in the mobile phone area
        row[42] = mobile_phone.split(';')[0]
        # if nothing held in other phone number, keep second mobile phone number - do we import this?
        if row[48] == '':
            row[48] = mobile_phone.split(';')[1]        
    
    # if two emails for contact in PCO, split, use the first in email, and the sceond in other email, preserving anything held in the business email cell
    if(";" in p_email):
        row[49] = p_email.split(';')[0]
        row[51] = p_email.split(';')[1]

    # if no personal email, but is business email, make it personal email
    if p_email == '' and b_email != '':
        row[49] = b_email
    elif p_email == '' and oth_email != '':
        row[49] = oth_email
    # if only other email is populated, insert it into primary email
    if p_email == '' and b_email == '' and oth_email != '':
        row[49] = oth_email

    # check for bad input - top level domain typos
    if row[49] != '':
        pre_domain = row[49][:-3]
        top_level_domain = row[49][-3:]
        domain_errors = ['omm', 'con', 'omn']
        if top_level_domain == 'omn' or top_level_domain == 'omn':
            row[49] = pre_domain + 'om'
        elif top_level_domain == 'con':
            row[49] = pre_domain + 'com'

    # convert PCO integers to the softer grades for HS
    try:
        grade = int(grade)
    except:
        # print(f'Cannot convert grade to int: {grade}')
        # if no grade given, use -2 as pco data begins at -1 for preschool
        grade = -2
    row[12] = convert_pco_grades(grade)

    # update PCO Ontario mistakes/specifics
    pco_prov_data = [';Ontario', 'AB;ON', 'ON;ON', 'ON;Ontario', 'ON/CANADA', 'Ontario', 'ONT', 'Onatrio', 'Ontario ;ON', 'on', 'On', 'Ont', 'ontario']

    if prov in pco_prov_data:
        row[30] = 'ON'
    elif prov == 'Nova Scotia':
        row[30] = 'NS' 
    elif prov == 'Sao Paulo':
        row[30] = ''
        row[29] = row[29]+', Sao Paulo'

    # translate memberships status
    if membership == 'Member':
        row[18] = 'I attend'
    elif membership == 'No longer attending Sanctus Church':
        row[18] = 'I no longer attend'
    elif membership == 'Occasional Attender':
        row[18] = 'I attend'
    elif membership == 'Regular Attender':
        row[18] = 'I attend'
    elif membership == 'Visitor':
        row[18] = 'I am a guest'

    if campus_name == '' and primary_site != '':
        row[21] = primary_site
    elif campus_name != '':
        row[21] = campus_name.replace('Sanctus Church ', '')

    if attending_since != '':
        date_str = attending_since
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(date_str, date_format)
        attending_since = start_date


'''Handler to clean the data, create a special id, and write to a file (called separately for PCO and Salesforce)'''
def update_contact_export(pco_export, pco_import):


    # open the export from pco
    with open(pco_export,'r',encoding = 'ISO-8859-1') as pcoexport:
        # create a file to recieve the updated information
        with open(pco_import, 'w') as pcoimport:
            # create the writer object
            writer = csv.writer(pcoimport)

            # lop through the data export
            for index, row in enumerate(csv.reader(pcoexport)): 
                
                # add emailId as first column
                if index == 0:
                    # print(f'mobile: {mobile_phone} home: {home_phone}')
                    row[91] = "Baptism Date"   
                    # add headers for special email id and the import source                      
                    writer.writerow(['EmailID']+row+['Import Source'])
                    
                # add special id for any subsequent rows after header
                else:
                    clean_pco_data(row) 
                    # after cleaning the data, grab the cells to use for special id
                      
                    f_name = row[4]  
                    l_name = row[7] 
                    p_email = row[49]  
                    b_email = row[50] 
                    oth_email = row[51]

                    # make special id
                    special_id = create_special_id(f_name, l_name, p_email, b_email, oth_email)
                    # write special id to the beginning of the sheet and import source at the end
                    writer.writerow([special_id]+row + ['PCO'])
   

if __name__ == '__main__':

    pco_export = 'PCO_People_raw.csv'
    pco_import = 'PCO_Contacts_cleaned.csv'
    pco_contact_house = 'PCO_Contacts_with_Household_associations.csv'
    pco_households = 'PCO_Households.csv'

    # for update_contact_export:
    # use either 'salesforce' or 'pco' as first parameter
    # use exported data filename as second parameter
    # use desired import data filename as third parameter

    # PCO
    update_contact_export(pco_export, pco_import)
    add_pco_household_label(pco_import, pco_contact_house)
    create_pco_household_csv(pco_contact_house, pco_households)