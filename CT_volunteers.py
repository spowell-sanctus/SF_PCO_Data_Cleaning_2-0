import csv
import utils.helpers


''' Opens the presorted list of groups exported from CT and creates a new csv with only those marked by a V or v to indicate a volunteer list'''
def sort_ct_groups(csv_input):
    # to store list of volunteer group ids
    volunteer_groups_ids = []
    # open the exported list that Sarah and Michelle sorted for type
    with open(csv_input, 'r', encoding='ISO-8859-1') as pre_sorted:
        # open a new csv that will hold only the volunteer groups
        with open('CT_volunteer_groups_list_final.csv', 'w') as v_out:
            writer = csv.writer(v_out)
            # loop through all the groups
            for index, row in enumerate(csv.reader(pre_sorted)):
                # write the headers to the new fils
                if index == 0:
                    writer.writerow(row)
                else:
                    # print(f'Running...{index}')
                    # if the row is indicated by a v
                    if row[0] == 'V' or row[0] == 'v':
                        # append the id to the list
                        volunteer_groups_ids.append(row[2])
                        # write the row to the new csv
                        writer.writerow(row)
                    # if there's a v but its not the only character in the cell - just to be safe
                    elif 'V' in row[0] or 'v' in row[0]:
                        print(f'Possible error on {index}:\n\t{row}\n')
    # return the list of volunteer groups' ids
    return volunteer_groups_ids


''' Open the roster of all people in all groups and if the id of the group they're in is in the volunteer group id list, write them to a new csv. The new csv can be sorted later by person, or by group.'''
def get_volunteer_rosters(volunteer_group_ids, all_ct_roster,pre_shaped_volunteer_list):
    # open the exported roster
    with open(all_ct_roster,'r',encoding='ISO-8859-1') as full_roster:
        # open the resulting list
        with open(pre_shaped_volunteer_list, 'w') as volunteers:

            writer = csv.writer(volunteers)
            # loop through the roster
            for index, row in enumerate(csv.reader(full_roster)):
                roster_group_id = row[1]
                # if the header row OR the id is present AND in the list of volunteer groups, write the row
                if index == 0 or roster_group_id != '' and roster_group_id in volunteer_group_ids:
                    writer.writerow(row)


''' Function to shape the historical volunteer data with special ID and do whatever else is necessary to import to HS '''
def shape_CT_like_PCO(pre_shaped_volunteer_list,final_CT_volunteer_file):
    
    with open(pre_shaped_volunteer_list, "r") as unshaped:
        with open(final_CT_volunteer_file, "a") as shaped:
            writer = csv.writer(shaped)

            for index, row in enumerate(csv.reader(unshaped)):
                row_to_write = []
                if index == 0:
                    row = ['Speical ID'] + row
                    writer.writerow(row)
                else: 
                    
                    fname = utils.helpers.get_letters_only(row[4].strip())
                    lname = utils.helpers.get_letters_only(row[3].strip())
                    email = utils.helpers.get_single_CT_email(row[13])
                    email_id = fname+lname+email
                    row = [email_id] + row
                    writer.writerow(row)
                    

if __name__ == "__main__":

    encoding='ISO-8859-1'

    # create a (static) list of groups characterized as volunteer 
    # v_csv_presort was created by Sarah Powell and Michelle Hartwick 
    v_csv_presort = 'CT_VolunteerGroups_31-05-23_sorted.csv'
    volunteer_group_ids = sort_ct_groups(v_csv_presort)

    # use the list of volunteers against the exported list of all group members from CT to get those in volunteer groups
    all_ct_roster = 'CT_Group_Members.csv'
    pre_shaped_volunteer_list = 'CT_volunteers_list.csv'
    get_volunteer_rosters(volunteer_group_ids,all_ct_roster,pre_shaped_volunteer_list)

    # make it look like PCO data for HS Upload
    final_CT_volunteer_file = 'CT_volunteers_list_final.csv'
    shape_CT_like_PCO(pre_shaped_volunteer_list,final_CT_volunteer_file)

