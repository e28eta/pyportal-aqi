A variant of PyPortal_AirQuality that pulls sensor data from PurpleAir for more up-to-date data, supporting averaging AQI from several sensors.

`secrets-example.py` has the various values expected by this project, including the `ssid` and `password` necessary for the PyPortal wifi-support. Rename it to `secrets.py` and fill it out with your configuration.

This project combines & customizes code from:

- [Adafruit's PyPortal_AirQuality](https://learn.adafruit.com/pyportal-air-quality-display/code-pyportal-with-circuitpython)
- [python-aqi](https://github.com/hrbonz/python-aqi)

### PurpleAir

PurpleAir has a documented API, which requires an API Key: https://api.purpleair.com
At the time of this update, the process for getting an API Key is to email contact@purpleair.com. More details at https://community.purpleair.com/t/making-api-calls-with-the-purpleair-api/180

Set `purpleair_sensors` in your `secrets.yml` to the list of sensors around you, joined with a comma `,`. The sensor ids can be found on the map, in the "Get this Widget" code.

### Circup

I've started using [circup](https://github.com/adafruit/circup) to manage libraries on the boards, and the `requirements.txt` shows the libraries & versions I'm using.

Install with `circup install -r requirements.txt`
