A variant of PyPortal_AirQuality that pulls sensor data from PurpleAir for more up-to-date data.

This project combines & customizes code from:

- [Adafruit's PyPortal_AirQuality](https://learn.adafruit.com/pyportal-air-quality-display/code-pyportal-with-circuitpython)
- [python-aqi](https://github.com/hrbonz/python-aqi)

It averages the AQI across multiple sensors, and averages the Lat/Long of those sensors for the displayed "location".

PurpleAir API docs seem to be here:
https://docs.google.com/document/d/15ijz94dXJ-YAZLi9iZ_RaBwrZ4KtYeCy08goGBwnbCU/edit

Set `purpleair_sensors` in your `secrets.yml` to the list of sensors around you, joined with the pipe character `|`. The sensor ids can be found on the map, in the "Get this Widget" code.

The "Get this Widget" link also includes a `key` parameter, and that can be included in the request by setting the `purpleair_token` secret. Looks like that could be used to view data from a private sensor, but I haven't tested this.
