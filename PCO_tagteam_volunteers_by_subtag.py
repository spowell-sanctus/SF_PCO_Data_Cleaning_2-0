# import the csv library
import csv
from datetime import datetime

from utils.helpers import get_valid_email,create_special_id


def clean_team_roster(active_file, save_file, team_name, tag_name):
    with open(active_file,'r', encoding = 'ISO-8859-1') as group_roster:
        with open(save_file,'w') as group_for_import:
            writer = csv.writer(group_for_import)

            for index, row in enumerate(csv.reader(group_roster)):
                if index == 0:
                    row = ['Speical Id']+['Team']+['Tag']+row
                    writer.writerow(row)
                else:     
                    f_name = (row[1].strip()).replace(' ','')
                    l_name = (row[2].strip()).replace(' ','')
                    p_email = row[3] 
                    b_email = row[4]
                    o_email = row[5]               
                    special_id = create_special_id(f_name,l_name,p_email,b_email,o_email)
                    row = [special_id] + [team_name] + [tag_name] + row
                    writer.writerow(row)


if __name__ == "__main__":

    active_file = 'WorshipTeam_Vocals.csv'
    team_name = 'Worship Team'
    tag_name = 'Vocals'
    today = datetime.now()
    day = today.strftime("%d")
    month = today.strftime("%B")
    year = today.strftime("%y")
    save_file = 'PCO_'+team_name+'_'+tag_name+'_'+day+month+year+'.csv'
   

    clean_team_roster(active_file, save_file, team_name, tag_name)
    