import os
from time import sleep

import requests


def call_pco(query):
    APP_ID = os.getenv('PCO_APP_ID')
    SECRET = os.getenv('PCO_SECRET')

    need_response = True

    while need_response:
        try:
            print(f'calling...')
            r = requests.get(query, auth=(APP_ID, SECRET))
            # dont include 4289 which is too many calls
            error_codes = [400, 401, 403, 404, 409, 422, 500, 503]
            got_error = r.status_code in error_codes
            too_many_error = 429
            if(r.status_code == too_many_error):
                print(f'Sleeping...')
                sleep(20)
                continue
            elif got_error:
                print(f'error...')
                need_response = False
                print(f'Error with response: {r.status_code}')
                r = False
                break
            else:
                need_response = False
        except requests.exceptions.RequestException as e:
            need_response = False
            print(f'Error in response: {e}')
            r = False 
            break

    return r

def get_next_link(response: dict):
    
    try:
        return response['links']['next']
    except KeyError:
        return False


def get_all_next_links(response):
    links = []       
    need_next = True
    while need_next:
        try:      
            next_link = get_next_link(response)
            if(next_link):
                links.append(next_link)
                response = call_pco(next_link).json() 
            else: 
                need_next = False
        except ValueError:
            print('There are no more links')
            need_next = False
    if len(links) > 0:
        return links
    else:
        return False


def get_previous_link(response: dict):
 
    try:
        return response['links']['previous']
    except KeyError:
        return False


def get_self_link(response: dict):
    
    try:
        return response['links']['self']
    except KeyError:
       return False