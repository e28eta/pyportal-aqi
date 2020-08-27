# -*- coding: utf-8 -*-

from aqi.constants import (POLLUTANT_PM25, POLLUTANT_PM10,
                          POLLUTANT_O3_8H, POLLUTANT_O3_1H,
                          POLLUTANT_CO_8H, POLLUTANT_SO2_1H,
                          POLLUTANT_NO2_1H, ALGO_EPA)

from aqi.algos import epa


def to_aqi(ccs, algo=ALGO_EPA):
    """Calculate the AQI based on a list of pollutants

    :param ccs: a list of tuples of pollutants concentrations with
                pollutant constant and concentration as values
    :type ccs: list
    :param algo: algorithm module name
    :type algo: str
    """
    return epa.AQI().aqi(ccs)
