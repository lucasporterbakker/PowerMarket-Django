from django.conf import settings

import requests


def dsire2_request(point, category='solar_technologies', technology='solar_photovoltaics'):
    """
    Generates request link for NREL DSIRE v2 and retrieves data from the API via GET/ request.
    Note: Works apparently only in the US.
    https://developer.nrel.gov/docs/electricity/energy-incentives-v2/
    :param point: GEOS point object with location of interest.
    :param category: defined by DSIRE (see link).
    :param technology: defined by DSIRE (see link).
    :return: JSON object { inputs: ..., metadata: ..., status: ..., result: ... }
    """

    lat, lng = point.coords

    # Construct API URL:
    api_url = 'https://developer.nrel.gov/api/energy_incentives/v2/dsire.json'
    api_url += '?api_key=%s' % settings.NREL_API_KEY
    api_url += '&lat=%s' % lat
    api_url += '&lon=%s' % lng
    api_url += '&category=%s' % category
    api_url += '&technology=%s' % technology

    response = requests.get(api_url)
    return response.json()
