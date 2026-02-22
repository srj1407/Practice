import requests
import os
from dotenv import load_dotenv

load_dotenv(r'C:\Users\SRJ\SRJ\Work\agentic_ai\.env')

MY_API_KEY = os.getenv('OPENWEATHER_API_KEY')
def get_weather(city_name):
    # Base URL for Current Weather Data
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Parameters: q = city, appid = your key, units = metric (for Celsius)
    params = {
        "q": city_name,
        "appid": MY_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(base_url, params=params)
        
        if(response):
            data = response.json()
        
            # Extracting specific data points
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            humidity = data['main']['humidity']
            
            result = {
                'temp': temp,
                'desc': desc,
                'humidity': humidity,
                'error': 'None'
            }
        else:
            result = {
                'error': 'Error calling weather API'
            }

        return result
        
    except requests.exceptions.HTTPError as err:
        return {
                'error': err
            }
    except Exception as err:
        return {
                'error': err
            }