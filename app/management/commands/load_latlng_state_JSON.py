# Python script to create JSON file of state codes mapped to state viewports in the US. 
# See this link for extensive documentation: https://purduecam2project.github.io/CAM2WebUI/implementationDetail/load_latlngJSON.html#
# Author: Matthew Fitzgerald & Deeptanshu Malik

from django.core.management.base import BaseCommand, CommandError
import urllib.request, urllib.parse, urllib.error
import requests
import ssl
from bs4 import BeautifulSoup
import json
from time import sleep

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    def get_states_from_webpage(self):
        #ignore SSL certificate errors
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        #get country select tag
        url = "http://www.cam2project.net/cameras/"
        html = urllib.request.urlopen(url, context=ctx).read()
        soup = BeautifulSoup(html, 'html.parser')
		country_menu = soup.find('select', id="country").select('United States')
        state_menu = soup.find('select', id="state").find_all('option')

        states = {}
        for state in state_menu:
            if state['value']:
                states[state['state']] =  str(state.text)

        return states
		
	def convert_states(self, states):
		statesdict = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming',
		'pa': 'Pennsylvania',
		'nm': 'New Mexico'
		}
		
		for stateabbrev, statefull in statesdict.items():
		i = 0
		while states 
			if states[i] == stateabbrev
				states[i] = statefull
			i++			

    def geocode_data(self, states):
        GOOGLE_MAPS_API_URL = 'http://maps.googleapis.com/maps/api/geocode/json'

        for state_code, state_name in states.items():
            #to enfore geocode 50 queries per second limit
            sleep(0.01)

            #make the request and get the response data
            req = requests.get(GOOGLE_MAPS_API_URL, params= {
                'address': state_name
            })
            res = req.json()

            if(res['status'] != 'OK'):
                print(state_code, state_name)
                continue
            else:
                sleep(1)
                req = requests.get(GOOGLE_MAPS_API_URL, params={
                    'address': state_name
                })
                res = req.json()
                if (res['status'] != 'OK'):
                    print("Failed 2nd attempt: ", state_code, state_name)
                    continue
                print("OK: ", state_code, state_name)

            #Use the first result
            result = res['results'][0]

            states[state_code] = result['geometry']['viewport']

        return states


    def handle(self, *args, **options):
        states = self.get_states_from_webpage()
		states = self.convertstates(states)
        states = self.geocode_data(states)

        with open('app/static/app/js/states_viewport.json', "w") as writeJSON:
            json.dump(states, writeJSON, indent=2)