import csv
from datetime import datetime

''' this program is designed to capture the errors in the initial import of SF_Contacts_w_Household_final_23-09-26 and SF_Households_final_23-09-26 by using an export of exising Companies to match up the Contacts with a Company using the original Salesforce Account ID and the new HubSpot record id. Once the contact that errored out from the import has been matched with the existing Company by address and name, the Household ID is updated to the existing Company ID. Then an UPDATE import can be run with SF_Extras_final_23-09-26. Deduplication still needs to happen (See Ewan Powell as an example.) '''   

def match_contact_with_existing_household(contacts, original_households,exported_households, final_w_house):
    
    with open(contacts, 'r', encoding = 'ISO-8859-1') as contact_file:
        for c_index, c_row in enumerate(csv.reader(contact_file)):
            contact_address = c_row[4]
            household_id = c_row[45] 
            
            # print(f'addy: {contact_address} house-id: {household_id}') 
                
            with open(original_households, 'r', encoding = 'ISO-8859-1') as households_file:
                for h_index, h_row in enumerate(csv.reader(households_file)):
                    household_id_number = h_row[0]
                    household_name = h_row[1]
                    if household_id_number.strip() == household_id.strip():
                        print(f'house-id: {household_id} id-no: {household_id_number} household_name: {household_name}')
                        
                        with open(exported_households, 'r') as exported_house:
                            for e_index, e_row in enumerate(csv.reader(exported_house)):
                                record_id = e_row[0]
                                record_name = e_row[7]
                                record_address = e_row[73]
                                
                                if record_name.strip() == household_name.strip() and contact_address.strip() == record_address.strip():
                                    print(f'household: {household_name} address: {record_address}')
                                    c_row[44] = ''
                                    c_row[45] = record_id
                                    
            with open (final_w_house, 'a') as sf_extra_final:
                writer = csv.writer(sf_extra_final)
                writer.writerow(c_row)
                  

if __name__ == '__main__':
    
    contacts = "SF_Contacts_Need_CompanyID.csv"
    origninal_households = "SF_Households_final_23-09-26.csv"
    exported_households = "SF_Companies_W_IDs.csv"
    final_w_house = "SF_Extras_final_23-09-26.csv"
    match_contact_with_existing_household(contacts, origninal_households, exported_households,final_w_house)