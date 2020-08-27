# -*- coding: utf-8 -*-

from aqi.constants import (POLLUTANT_PM25, POLLUTANT_PM10,
                          POLLUTANT_O3_8H, POLLUTANT_O3_1H,
                          POLLUTANT_CO_8H, POLLUTANT_SO2_1H,
                          POLLUTANT_NO2_1H)
from aqi.algos.base import PiecewiseAQI


class AQI(PiecewiseAQI):
    """Implementation of the EPA AQI algorithm.
    """

    piecewise = {
        'aqi': [
            (0, 50),
            (51, 100),
            (101, 150),
            (151, 200),
            (201, 300),
            (301, 400),
            (401, 500)],
        'bp': {
            POLLUTANT_O3_8H: [
                (float('0.000'), float('0.059')),
                (float('0.060'), float('0.075')),
                (float('0.076'), float('0.095')),
                (float('0.096'), float('0.115')),
                (float('0.116'), float('0.374')),
            ],
            POLLUTANT_O3_1H: [
                (0, 0),
                (0, 0),
                (float('0.125'), float('0.164')),
                (float('0.165'), float('0.204')),
                (float('0.205'), float('0.404')),
                (float('0.405'), float('0.504')),
                (float('0.505'), float('0.604')),
            ],
            POLLUTANT_PM10: [
                (float('0'), float('54')),
                (float('55'), float('154')),
                (float('155'), float('254')),
                (float('255'), float('354')),
                (float('355'), float('424')),
                (float('425'), float('504')),
                (float('505'), float('604')),
            ],
            POLLUTANT_PM25: [
                (float('0.0'), float('12.0')),
                (float('12.1'), float('35.4')),
                (float('35.5'), float('55.4')),
                (float('55.5'), float('150.4')),
                (float('150.5'), float('250.4')),
                (float('250.5'), float('350.4')),
                (float('350.5'), float('500.4')),
            ],
            POLLUTANT_CO_8H: [
                (float('0.0'), float('4.4')),
                (float('4.5'), float('9.4')),
                (float('9.5'), float('12.4')),
                (float('12.5'), float('15.4')),
                (float('15.5'), float('30.4')),
                (float('30.5'), float('40.4')),
                (float('40.5'), float('50.4')),
            ],
            POLLUTANT_SO2_1H: [
                (float('0'), float('35')),
                (float('36'), float('75')),
                (float('76'), float('185')),
                (float('186'), float('304')),
                (float('305'), float('604')),
                (float('605'), float('804')),
                (float('805'), float('1004')),
            ],
            POLLUTANT_NO2_1H: [
                (float('0'), float('53')),
                (float('54'), float('100')),
                (float('101'), float('360')),
                (float('361'), float('649')),
                (float('650'), float('1249')),
                (float('1250'), float('1649')),
                (float('1650'), float('2049')),
            ],
        },
        'prec': {
            POLLUTANT_O3_8H: 3,
            POLLUTANT_O3_1H: 3,
            POLLUTANT_PM10: 0,
            POLLUTANT_PM25: 1,
            POLLUTANT_CO_8H: 1,
            POLLUTANT_SO2_1H: 0,
            POLLUTANT_NO2_1H: 0,
        },
        'units': {
            POLLUTANT_O3_8H: 'ppm',
            POLLUTANT_O3_1H: 'ppm',
            POLLUTANT_PM10: 'µg/m³',
            POLLUTANT_PM25: 'µg/m³',
            POLLUTANT_CO_8H: 'ppm',
            POLLUTANT_SO2_1H: 'ppb',
            POLLUTANT_NO2_1H: 'ppb',
        },
    }
