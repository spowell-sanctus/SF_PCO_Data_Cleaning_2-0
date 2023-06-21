import csv
from datetime import datetime
import re
import string

from utils.helpers import convert_numbers_to_boolean, create_special_id, convert_pco_grades, get_letters_only, get_valid_email


''' Write the rows of data for the final contacts with household associations file for import'''
def loop_through_contacts_update_label(salesforce_import,salesforce_final_contact_household_import,primary_contact_id, household_id, household_name):
                
        # create a file to recieve the updated information
        with open(salesforce_import, 'r', encoding = 'ISO-8859-1') as salesforce_import:
            # create the writer object           
    
                for index, row in enumerate(csv.reader(salesforce_import)):
                    # create holder for the row data to pull from the cleaned data
                    row_to_write = ''
                    # if not the header row - that was created in write_final_sf_contact_households_header_row
                    if index != 0:
                        # write the row with the association label at 197 and the household id at 198, and the source at 199
                        if row[1] == primary_contact_id and row[197] == '' and row[198] == '':
                            row_to_write = row+['Primary Household Contact']+[household_id]+['SF']
                        elif row[4] == household_id and row[197] == '' and row[198] == '':
                            row_to_write = row+['Other Household Member']+[household_id]+['SF']
                        
                    if row_to_write != '':
                        with open (salesforce_final_contact_household_import, 'a') as sf_final:
                                writer = csv.writer(sf_final)
                                writer.writerow(row_to_write)


''' Write the header row for the final file used to import contacts with household associations '''
def write_final_sf_contact_households_header_row(salesforce_import,salesforce_final_contact_household_import):
           # create a file to recieve the updated information
    with open(salesforce_import, 'r') as salesforce_import:
            
            # create a file to recieve the updated information
        with open(salesforce_final_contact_household_import, 'w') as sf_final:
            writer = csv.writer(sf_final)
            for index, row in enumerate(csv.reader(salesforce_import)):
                if index == 0:
                    writer.writerow(row)
                    break


''' Write the header row for the final file used to import contacts with household associations '''
def create_sf_households_final(households_raw, households_final):
           # create a file to recieve the updated information
    with open(households_raw, 'r',encoding = 'ISO-8859-1') as households_raw:
            
            # create a file to recieve the updated information
        with open(households_final, 'w+') as sf_house_final:
            writer = csv.writer(sf_house_final)
            for index, row in enumerate(csv.reader(households_raw)):
                if index == 0:
                    row = ['Household Id']+row[1:]
                    print(row)
                    writer.writerow(row)
                else: 
                    writer.writerow(row)
 
'''Creates a new file that hold the records for Households, one per primary contact on the contact data'''
def create_sf_household_label(households_raw, households_final, salesforce_import,salesforce_final_contact_household_import):     

    write_final_sf_contact_households_header_row(salesforce_import,salesforce_final_contact_household_import)

    create_sf_households_final(households_raw, households_final)

     # open the export
    with open(households_raw,'r+',encoding = 'ISO-8859-1') as households_raw:  
            starttime = datetime.now()
            for index, row in enumerate(csv.reader(households_raw)):
                
                primary_contact_id = row[47]
                household_name = row[3]
                household_id = row[0]
                if primary_contact_id != 'npe01__One2OneContact__c':
                    
                    loop_through_contacts_update_label(salesforce_import,salesforce_final_contact_household_import,primary_contact_id, household_id, household_name)
                    print(f"running... {index}")
    
    endtime= datetime.now()
    delta = endtime - starttime
    print(f'Run Time: {delta}')
    
    

'''Cleans the data from Salesforce export for import into HubSpot contacts (no associations)'''
def clean_salesforce_data(row):
  
    do_not_call = row[41]  
    media_consent = row[189]
    province_state = row[18]
    membership_status = row[176]
    is_deceased = row[123]  
    do_not_contact = row[124]
    email_optout = row[39] 

    # turn 0 into false, and 1 into true
    row[189] = convert_numbers_to_boolean(media_consent)
    row[41] = convert_numbers_to_boolean(do_not_call)
    row[123] = convert_numbers_to_boolean(is_deceased)
    row[124] = convert_numbers_to_boolean(do_not_contact)
    row[39] = convert_numbers_to_boolean(email_optout)

    # update SF Ontario mistakes
    sf_prov_mistakes = ['On', 'Ontario', '9', 'Canada', 'Ontario (ON)', 'ontario', 'Ontarip', 'ONT', 'Ont', 'OnON', 'Onterio','State (US Residents)*']

    if province_state in sf_prov_mistakes:
        row[18] = 'ON'
    elif province_state == 'Ajax':
        row[17] = 'Ajax'
        row[18] = 'ON'
    elif province_state == 'Peterborough':
        row[17] = 'Peterborough'
        row[18] = 'ON'
    elif province_state == 'Ga':
        row[18] = "GA"
    elif province_state == 'PEI':
        row[18] = 'PE'
    
    # update salesforce statuses
    if membership_status == 'Regular Attender':
        row[176] = 'I attend'
    elif membership_status == 'Visitor':
        row[176] = 'I am a guest'


'''Handler to clean the data, create a special id, and write to a file (called separately for PCO and Salesforce)'''
def update_contact_export(export_filename, updated_filename):
    # open the export from pco
    with open(export_filename,'r',encoding = 'ISO-8859-1') as csvinput:
        # create a file to recieve the updated information
        with open(updated_filename, 'w') as csvoutput:
            # create the writer object
            writer = csv.writer(csvoutput)

            # lop through the data export
            for index, row in enumerate(csv.reader(csvinput)): 
                    
                # add emailId as first column
                if index == 0:
                    # add the necessary headers for the special id, association label, household id, and the import source of "SF"                       
                    writer.writerow(['EmailID']+row + ['Association Label']+['Household Id']+['Import Source'])
                    
                # add special id for any subsequent rows after header
                else:
                   
                    clean_salesforce_data(row)
  
                    f_name = row[5]  
                    l_name = row[6] 
                    p_email = row[31] # col AF/32
                    alt_email = row[58] # col BG/59

                    # make special id
                    special_id = create_special_id(f_name, l_name, p_email,'',alt_email)
                    # write special id to the beginning of the sheet
                    writer.writerow([special_id]+row+['SF'])
   

if __name__ == '__main__':

    salesforce_export = 'SF_Contacts_raw.csv'
    salesforce_cleaned = 'SF_Contacts_cleaned.csv'
    salesforce_final_contact_household_import = 'SF_Contacts_with_Household_associations.csv'
    salesforce_households_raw = 'SF_Households_raw.csv'
    salesforce_households_final = 'SF_Households_final.csv'

    # for update_contact_export:
    # use either 'salesforce' or 'pco' as first parameter
    # use exported data filename as second parameter
    # use desired import data filename as third parameter

    # SF
    update_contact_export(salesforce_export, salesforce_cleaned)
    # long run - about 32 minutes
    create_sf_household_label(salesforce_households_raw, salesforce_households_final, salesforce_cleaned,salesforce_final_contact_household_import)

 