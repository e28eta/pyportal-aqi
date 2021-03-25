# -*- coding: utf-8 -*-

class BaseAQI(object):
    """A generic AQI class"""

    def iaqi(self, elem, cc):
        """Calculate an intermediate AQI for a given pollutant. This is
        the heart of the algo. Return the IAQI for the given pollutant.

        .. warning:: the concentration is passed as a string so
        :class:`decimal.Decimal` doesn't act up with binary floats.

        :param elem: pollutant constant
        :type elem: int
        :param cc: pollutant concentration (µg/m³ or ppm)
        :type cc: str
        """
        raise NotImplementedError

    def aqi(self, ccs, iaqis=False):
        """Calculate the AQI based on a list of pollutants. Return an
        AQI value, if `iaqis` is set to True, send back a tuple
        containing the AQI and a dict of IAQIs.

        :param ccs: a list of tuples of pollutants concentrations with
                    pollutant constant and concentration as values
        :type ccs: list
        :param iaqis: return IAQIs with result
        :type iaqis: bool
        """
        _iaqis = {}
        for (elem, cc) in ccs:
            _iaqi = self.iaqi(elem, cc)
            if _iaqi is not None:
                _iaqis[elem] = _iaqi
        _aqi = max(_iaqis.values())
        if iaqis:
            return (_aqi, _iaqis)
        else:
            return _aqi

    def cc(self, elem, iaqi):
        """Calculate a concentration for a given pollutant. Return the
        concentration for the given pollutant based on the intermediate AQI.

        .. warning:: the intermediate AQI is passed as a string

        :param elem: pollutant constant
        :type elem: int
        :param cc: intermediate AQI
        :type cc: str
        """
        raise NotImplementedError


class PiecewiseAQI(BaseAQI):
    """A piecewise function AQI class (like EPA or MEP)"""

    piecewise = None

    def iaqi(self, elem, cc):
        if self.piecewise is None:
            raise NameError("piecewise struct is not defined")
        if elem not in self.piecewise['bp'].keys():
            return None

        _cc = round(float(cc), self.piecewise['prec'][elem])

        # define breakpoints for this pollutant at this concentration
        bps = self.piecewise['bp'][elem]
        aqis = self.piecewise['aqi']

        # Handle out-of-range values by clamping to lowest/highest value
        if _cc < bps[0][0]:
            return float(aqis[0][0])
        if _cc > bps[-1][1]:
            return float(aqis[-1][1])

        # otherwise find correct range
        bplo = None
        bphi = None
        idx = 0
        for bp in bps:
            if _cc >= bp[0] and _cc <= bp[1]:
                bplo = bp[0]
                bphi = bp[1]
                break
            idx += 1
        # get corresponding AQI boundaries
        (aqilo, aqihi) = aqis[idx]

        # equation
        value = (aqihi - aqilo) / (bphi - bplo) * (_cc - bplo) + aqilo
        return round(value)


    def cc(self, elem, iaqi):
        if self.piecewise is None:
            raise NameError("piecewise struct is not defined")
        if elem not in self.piecewise['bp'].keys():
            return None

        _iaqi = int(iaqi)

        # define aqi breakpoints for this pollutant at this IAQI
        bps = self.piecewise['aqi']
        bplo = None
        bphi = None
        idx = 0
        for bp in bps:
            if _iaqi >= bp[0] and _iaqi <= bp[1]:
                bplo = bp[0]
                bphi = bp[1]
                break
            idx += 1
        # get corresponding concentration boundaries
        (cclo, cchi) = self.piecewise['bp'][elem][idx]

        # equation
        value = (cchi - cclo) / (bphi - bplo) * (_iaqi - bplo) + cclo
        return round(value, self.piecewise['prec'][elem])
