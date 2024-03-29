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
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.bitmap_label import Label
from adafruit_requests import OutOfRetries
from adafruit_pyportal import PyPortal
import aqi

import microcontroller

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# See https://api.purpleair.com/#api-sensors-get-sensors-data
DATA_SOURCE = ("https://api.purpleair.com/v1/sensors"
               # comma separated list of sensor IDs
               "?show_only=" + secrets['purpleair_sensors'] +
               # updated in last hour, since my display is supposed to be near-real-time
               "&max_age=3600"
               # fields used in calc_aqi_from_purpleair
               "&fields=pm2.5_atm,pm10.0_atm")

LAST_UPDATE = None

"""
Purple Air gives pm 2.5 and pm 10.0 values. Using the EPA algorithm from
python-aqi to translate those into AQI numbers.

Note: I have not evaluated any of the data available in v1 of the API, simply
ported over existing code from the older API. Ref: https://api.purpleair.com/#api-sensors-get-sensors-data
"""
def calc_aqi_from_purpleair(json_dict):
    global LAST_UPDATE
    aqis = []

    status_label.text = 'p' # parsing

    # Burn some CPU cycles on every response to future-proof, although their API should
    # always return data in the same order it was requested
    try:
        fields = json_dict['fields']
        field_count = len(fields)
        pm2_5_atm = fields.index('pm2.5_atm')
        pm10_0_atm = fields.index('pm10.0_atm')
    except ValueError as e:
        print("ValueError while parsing response:", e)
        raise e

    for result in json_dict['data']:
        if not (len(result) >= field_count): continue

        this_aqi = aqi.to_aqi([
            (aqi.POLLUTANT_PM25, result[pm2_5_atm]),
            (aqi.POLLUTANT_PM10, result[pm10_0_atm])
        ])
        aqis.append(this_aqi)

    # Stick average AQI into JSON so that PyPortal's `json_path` can find it
    if (len(aqis) > 0):
        json_dict['avg_aqi'] = sum(aqis) / len(aqis)
    else:
        json_dict['avg_aqi'] = 'Unknown'
    if json_dict['data_time_stamp']:
        try:
            LAST_UPDATE = time.localtime(json_dict['data_time_stamp'])
        except:
            LAST_UPDATE = None

# the current working directory (where this file is)
cwd = ("/"+__file__).rsplit('/', 1)[0]
# workaround for https://github.com/adafruit/Adafruit_CircuitPython_PyPortal/issues/121
caption_font = bitmap_font.load_font(cwd+"/fonts/HelveticaNeue-24.bdf")
caption_label = Label(caption_font,
                      text="",
                      scale=1,
                      color=0x000000,
                      anchor_point=(0.5, 1.0),
                      anchored_position=(160, 230)
                      )

status_font = bitmap_font.load_font(cwd+"/fonts/Helvetica-Bold-16.bdf")
status_label = Label(status_font,
                     text="i", # initializing
                     scale=1,
                     color=0xFFFFFF,
                     anchor_point=(1.0, 0),
                     anchored_position=(310, 10)
                     )

# Initialize the pyportal object and let us know what data to fetch and where
# to display it
pyportal = PyPortal(url=DATA_SOURCE,
                    headers={'X-API-Key': secrets['purpleair_token']},
                    json_path=['avg_aqi'],
                    json_transform=calc_aqi_from_purpleair,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=0x000000,
                    text_font=cwd+"/fonts/Helvetica-Bold-100.bdf",
                    text_position=(90, 100),
                    text_color=0x000000,
                    )
pyportal.splash.append(caption_label)
pyportal.splash.append(status_label)

SLEEP_TIME_SECONDS = 10*60  # wait 10 minutes between updates
RESET_INTERVAL_SECONDS = (1 << 21) # approx 2^31 ms

while True:
    if time.monotonic() >= RESET_INTERVAL_SECONDS:
        # reset every ~24 days, hypothesis that something is having problems with >32 bit tick values
        microcontroller.reset()

    try:
        status_label.text = 'f' # fetching
        value = pyportal.fetch()
        status_label.text = 'u' # updating UI
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

        if isinstance(LAST_UPDATE, time.struct_time):
            caption_label.text = 'at {:02}:{:02}:{:02} UTC on {}/{}'.format(LAST_UPDATE.tm_hour, LAST_UPDATE.tm_min, LAST_UPDATE.tm_sec,
                                                                            LAST_UPDATE.tm_mon, LAST_UPDATE.tm_mday)
        else:
            caption_label.text = '<unknown data_time_stamp>'
    except ValueError as e:
        # Possibly PurpleAir is having load problems.
        # See https://github.com/e28eta/pyportal-aqi/issues/1
        print("ValueError occurred, retrying! -", e)
    except RuntimeError as e:
        print("Some RuntimeError occurred, retrying! -", e)
    except OSError as e:
        print("Some OSError occurred, retrying! -", e)
    except OutOfRetries as e:
        # https://github.com/adafruit/Adafruit_CircuitPython_Requests/blob/8a19521fa624aa1150471ea2b066cee1d91ae296/adafruit_requests.py#L165
        print("OutOfRetries error thrown by requests - ", e)

    status_label.text = 's' # sleeping
    time.sleep(SLEEP_TIME_SECONDS)
