"""
This uses PyPortal and python-aqi to display AQI, pulling data from
purpleair.com.

Adapted from:
https://github.com/adafruit/Adafruit_Learning_System_Guides/tree/master/PyPortal_AirQuality

The license on PyPortal_AirQuality is the MIT License

Copyright (c) 2018 Adafruit Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
import time
import board
from adafruit_pyportal import PyPortal
import aqi

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Set up where we'll be fetching data from
DATA_SOURCE = "https://www.purpleair.com/json"
DATA_SOURCE += "?show=" + secrets['purpleair_sensors']
DATA_SOURCE += "&key=" + secrets['purpleair_token']

AVG_LAT = None
AVG_LONG = None

"""
Purple Air gives pm 2.5 and pm 10.0 values. Using the EPA algorithm from
python-aqi to translate those into AQI numbers.
Also, while iterating through the purpleair sensor results, compute the avg
lat/long for display.
"""
def calc_aqi_from_purpleair(json_dict):
    global AVG_LAT, AVG_LONG
    aqis, lats, longs = [], [], []

    for result in json_dict['results']:
        if result['pm2_5_atm']:
            # I haven't tested how this works if pm10 is missing
            this_aqi = aqi.to_aqi([
                (aqi.POLLUTANT_PM25, result['pm2_5_atm']),
                (aqi.POLLUTANT_PM10, result['pm10_0_atm'])
            ])
            aqis.append(this_aqi)

            # I chose sensors from the public map, they all had valid Lat/Lon
            if result['Lat']:
                lats.append(result['Lat'])
            if result['Lon']:
                longs.append(result['Lon'])

    # Stick average AQI into JSON so that PyPortal's `json_path` can find it
    json_dict['avg_aqi'] = sum(aqis) / len(aqis)

    if len(lats) > 0 and len(longs) > 0:
        # Update global value of avg lat/long so we can update the caption
        AVG_LAT = sum(lats) / len(lats)
        AVG_LONG = sum(longs) / len(longs)

# the current working directory (where this file is)
cwd = ("/"+__file__).rsplit('/', 1)[0]
# Initialize the pyportal object and let us know what data to fetch and where
# to display it
pyportal = PyPortal(url=DATA_SOURCE,
                    json_path=['avg_aqi'],
                    json_transform=calc_aqi_from_purpleair,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=0x000000,
                    text_font=cwd+"/fonts/Helvetica-Bold-100.bdf",
                    text_position=(90, 100),
                    text_color=0x000000,
                    # pad caption string so there's room for lat/long later
                    caption_text="Air Quality Index              ",
                    caption_font=cwd+"/fonts/HelveticaNeue-24.bdf",
                    caption_position=(15, 220),
                    caption_color=0x000000,)

while True:
    try:
        value = pyportal.fetch()
        print("Response is", value)
        if 0 <= value <= 50:
            pyportal.set_background(0x66bb6a)  # good
        if 51 <= value <= 100:
            pyportal.set_background(0xffeb3b)  # moderate
        if 101 <= value <= 150:
            pyportal.set_background(0xf39c12)  # sensitive
        if 151 <= value <= 200:
            pyportal.set_background(0xff5722)  # unhealthy
        if 201 <= value <= 300:
            pyportal.set_background(0x8e24aa)  # very unhealthy
        if 301 <= value <= 500:
            pyportal.set_background(0xb71c1c)  # hazardous

        if AVG_LAT and AVG_LONG:
            pyportal.set_caption('AQI for ({0:5.2f}, {1:6.2f})'
                                 .format(AVG_LAT, AVG_LONG),
                                 (15, 220), 0x000000)

    except RuntimeError as e:
        print("Some error occured, retrying! -", e)

    time.sleep(10*60)  # wait 10 minutes before getting again