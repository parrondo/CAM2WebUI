# load_latlng_state_JSON

## What is it
It is a custom Django command to execute the load_latlng_state_JSON.py script. 

Main purpose of this script is to create a dictionary in the form a JSON object to proivde O(1) lookup for latitudinal and longitudinal information of  northeast and southwest corners of a specific state in the United States. This documentation, script, and informtion is directly adapted from load_latlngJSON by Deeptanshu Malik. This information is needed to dynamically adjust viewport of map as multiple countries are selected.

This command is used to execute a scripts that parses all countries listed on our project's cameras webpage, uses geocode API to obtain viewport of each country, and then creates a JSON file of country codes mapped to country viewports.

## Why it was needed
See [this issue](https://github.com/PurdueCAM2Project/CAM2WebUI/issues/95) for an in-depth explanation.

A brief summary: this script is a necessary solution to 
1. Limit calls to geocode API: there's a limit to number of free requests to geocode API which would have been undoubtedly exceeded in times of relatively heavy traffic to our website.
2. Increase speed performace of our website's cameras page: geocoder API requests may take several hundered milliseconds and this results in a subpar user experience when multiple countries are selected, in fact, dynaymically adjusting viewport when more than 3 countries are selected becomes infeasbile

## Executing the script

```
python manage.py load_latlng_state_JSON
```

This will print relevant message to to the console for each country as it is successfully, or not, geocoded. If this is not desired then the output can be piped to a dummy file where it can be examined. 

```
python manage.py load_latlng_state_JSON > dummy.txt
```

The script can run for potentially more than 2 minutes, due to reasons explained [here](#delay_reason) and [here](https://github.com/PurdueCAM2Project/CAM2WebUI/commit/b725343182ae964cbd2a3a44cb72d379a11b4c2e).

## Documentation

The script was setup as per the [official tutorial](https://docs.djangoproject.com/en/dev/howto/custom-management-commands/) on how to create a custom Django command.

The path to the script: /app/management/commands/load_latlngJSON.py

<div class="admonition note">
<p class="first admonition-title">Note</p>
<p class="last"Tthe path to the script, the 'Command' class definition and the 'handle' member function definition must not be modified as they are necessary for the custom command to be recognized by Django.
.</p>
</div>

Each time the script is executed, the handle member funtion of the Command class is called

```
    def handle(self, *args, **options):
        states = self.get_states_from_webpage()
		states = self.convertstates(states)
        states = self.geocode_data(states)

        with open('app/static/app/js/states_viewport.json', "w") as writeJSON:
            json.dump(states, writeJSON, indent=2)
```
#### Using Beautiful Soup to parse webpage

As explained in the [CAM2 Training docs](https://github.com/PurdueCAM2Project/Training#introduction-to-beautiful-soup-and-selenium), Beautiful Soup was used to parse the list of countries for our website's cameras page.

[This](http://web.stanford.edu/~zlotnick/TextAsData/Web_Scraping_with_Beautiful_Soup.html) webpage from stanford.edu is also an excellent quick guide to Beautiful Soup
```
import urllib.request, urllib.parse, urllib.error
import ssl
from bs4 import BeautifulSoup
```
```
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
```

#### Using geocode API
Google's geocode API was used to obtain viewports of the states listed on our website's drop down menu for the United States (currently). 

These viewports are nested dictionaries containing information about the latitudinal and longitudinal positions of the northwest and southwest corners of a country.

[This](https://gist.github.com/pnavarrc/5379521) tutorial on Github was referred to as a guide to use geocode API in python.

The geocoding function takes a dictionary of country codes mapped to country names as inputs and makes requests using country names to obtain viewports. Each country's code is then mapped to country's viewport. The resulting dictionary is then returned.

- It is necessary for the script to sleep for 0.01 secounds before making a request to geocode API in order to ensure that the 50 queries per second limit is not exceeded.
- <a name="delay_reason">Initially not all countries were geocoded properly, each time geocoding randomly failed for a number of consecutively listed countries. This was solved by waiting for 1 second in the event of failure and then sending the same request to geocode API again. Now 100% of the countries are geocoded each time the script is executed. However, as a consequence, the script may take more than 2 minutes to run.</a>

```
import requests
from time import sleep
```
```
    
```
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
    ```

#### Parsing the State Codes
I created a dict to match all of the state codes that are listed in the dropdown with something the geocode API would understand:

```
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
```

#### Creating JSON file

Once the nested dictionary of country codes mapped to country viewports is obtained, 'json' library is used to create a JSON file of this dictionary in the appropriate directory:

```
import json
```
```
with open('app/static/app/js/countries_viewport.json', "w") as writeJSON:
    json.dump(countries, writeJSON)
```
