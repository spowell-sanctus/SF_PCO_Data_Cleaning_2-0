import csv
from datetime import datetime
import pandas as pd

from utils.helpers import get_now, convert_numbers_to_boolean, create_special_id, runtime, remove_unneeded_columns, write_response_file


''' Write the rows of data for the final contacts with household associations file for import'''
def loop_through_contacts_update_label(salesforce_import,salesforce_final_contact_household_import,primary_contact_id, household_id, household_name):
        # print(f'\n{primary_contact_id}\t{household_id}\t{household_name}')
        # create a file to recieve the updated information
        with open(salesforce_import, 'r', encoding = 'ISO-8859-1') as salesforce_import:
            # create the writer object           
    
                for index, row in enumerate(csv.reader(salesforce_import)):
                    # create holder for the row data to pull from the cleaned data
                    row_to_write = ''
                    # if not the header row - that was created in write_final_sf_contact_households_header_row                    
                    if index != 0:
                        # print(f'0: {row[0]}\t1: {row[1]}')
                        # write the row with the association label at 42 and the household id at 43, and the source at 44
                        # if the primary_contact_id from household matches the contact Id row, it's a primary contact
                        if row[0] == primary_contact_id and row[43] == '' and row[44] == '':
                            # print(f'1. {row}')
                            row_to_write = row+['Primary Household Contact']+[household_id]+['SF']
                        # if the account id of the person matches the household ID must have a secondary member
                        elif row[1] == household_id and row[43] == '' and row[44] == '':
                            # print(f'2. {row}')
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
                    # print(row)
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
                
                # data from households export
                primary_contact_id = row[9]
                household_name = row[1]
                household_id = row[0]
                
                # if index == 0:
                #     print(f'\n{primary_contact_id}\t{household_name}\t{household_id}')
                if primary_contact_id != 'npe01__One2OneContact__c':
                    # passing the data from the households export
                    loop_through_contacts_update_label(salesforce_import,salesforce_final_contact_household_import,primary_contact_id, household_id, household_name)
                    # print(f"running... {index}")
    
    endtime = datetime.now()
    delta = endtime - starttime
    print(f'Run Time: {delta}')
    
    

'''Cleans the data from Salesforce export for import into HubSpot contacts (no associations)'''
def clean_salesforce_data(row):
    
    province_state = row[6]
    email_optout = row[15] 
    do_not_call = row[16]
    last_modified = row[17] 
    is_deceased = row[32]  
    do_not_contact = row[33] 
    epi_pen_carried = row[35]
    membership_status = row[42]
    gifts = row[43]
    media_consent = row[44]

    # turn 0 into false, and 1 into true
    row[15] = convert_numbers_to_boolean(email_optout)
    row[16] = convert_numbers_to_boolean(do_not_call)
    row[32] = convert_numbers_to_boolean(is_deceased)
    row[33] = convert_numbers_to_boolean(do_not_contact)
    row[35] = convert_numbers_to_boolean(epi_pen_carried)
    row[44] = convert_numbers_to_boolean(media_consent)
   
    # if gifts include "Interpretation", update to "Interpretation of Tongues" to be read by dropdown; add a ';' to front of the list
    if gifts != '':
        gifts = gifts.replace('Interpretation', 'Interpretation of Tongues')        
        gifts = ';' + gifts
        row[43] =  gifts
        

    # update SF Ontario mistakes
    sf_prov_mistakes = ['On', 'Ontario', '9', 'Canada', 'Ontario (ON)', 'ontario', 'Ontarip', 'ONT', 'Ont', 'OnON', 'Onterio','State (US Residents)*']

    if province_state in sf_prov_mistakes:
        row[6] = 'ON'
    elif province_state == 'Ajax':
        row[5] = 'Ajax'
        row[6] = 'ON'
    elif province_state == 'Peterborough':
        row[5] = 'Peterborough'
        row[6] = 'ON'
    elif province_state == 'Ga':
        row[6] = "GA"
    elif province_state == 'PEI':
        row[6] = 'PE'
    
    # update salesforce statuses
    if membership_status == 'Regular Attender':
        row[42] = 'I attend'
    elif membership_status == 'Visitor':
        row[42] = 'I am a guest'


'''Handler to clean the data, create a special id, and write to a file'''
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
                    # province_state = row[6]
                    # email_optout = row[15] 
                    # do_not_call = row[16]
                    # last_modified = row[17] 
                    # is_deceased = row[32]  
                    # do_not_contact = row[33] 
                    # epi_pen_carried = row[35]
                    # membership_status = row[42]
                    # gifts = row[43]
                    # media_consent = row[44]
                    # print(f'\n{do_not_call}\n{media_consent}\n{province_state}\n{membership_status}\n{do_not_call}\n{last_modified}\n{is_deceased}\n{do_not_contact}\n{email_optout}\n{gifts}\n{epi_pen_carried}')
                    
                    row[17] = 'Source Last Modified Date'
                    
                    # add the necessary headers for the special id, association label, household id, and the import source of "SF"                       
                    writer.writerow(row + ['Association Label']+['Household Id']+['Import Source'])
                    
                # add special id for any subsequent rows after header
                else:
                   
                    clean_salesforce_data(row)

                    id = row[0]
                    f_name = row[2]  
                    l_name = row[3] 
                    p_email = row[13] # col AF/32
                    alt_email = row[17] # col BG/59                  
                                        

                    # make special id
                    # special_id = create_special_id(f_name, l_name, p_email,'',alt_email)
                    # write special id to the beginning of the sheet
                    # writer.writerow([special_id]+row)    
                    writer.writerow(row)    
   

if __name__ == '__main__':

    # columns we dont' need
    contacts_drop_sheet = 'SF_Contact_Columns_Ignore.csv'
    household_drop_sheet = 'SF_Household_Columns_Ignore.csv'
    
    # export of all contacts from Salesforce
    salesforce_export = 'SF_Contacts_raw_23-10-02.csv'
    # export of all households from Salesforce
    salesforce_households_raw = 'SF_Households_raw_23-10-02.csv'
    
    # filenames to use for after extra columns have been removed
    salesforce_contacts_columns_clean = 'SF_Contact_Necessary_Columns_Raw_23-10-02.csv'
    salesforce_household_columns_clean = 'SF_Household_Necessary_Columns_Raw_23-10-02.csv'
    
    # filename to use for file after its been cleaned
    salesforce_cleaned = 'SF_Contacts_cleaned_23-10-02.csv'
    
    # filename to use for file after households have been associated
    salesforce_final_contact_household_import = 'SF_Contacts_w_Household_final_23-10-02.csv'
    
    # filename to use for households after cleaning
    salesforce_households_final = 'SF_Households_final_23-10-02.csv'

    # logging start time
    start = get_now('Start Time')
    
    # SF
    # remove uncessary columns from contacts export
    remove_unneeded_columns(salesforce_export, contacts_drop_sheet, salesforce_contacts_columns_clean)
    # remove uncessary columns from households export
    remove_unneeded_columns(salesforce_households_raw, household_drop_sheet, salesforce_household_columns_clean)
        
    # # clean the contacts file - formatting etc.
    update_contact_export(salesforce_contacts_columns_clean, salesforce_cleaned)
    
    # # create households from contacts data (shorter run with fewer columns - about 10 minutes - with all columns, a long run - about 35 minutes)
    create_sf_household_label(salesforce_household_columns_clean, salesforce_households_final, salesforce_cleaned,salesforce_final_contact_household_import)

    # logging endtiem
    end = get_now('End Time')
    
    # logging run time
    runtime(start, end)
    