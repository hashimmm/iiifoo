"""This module provides mock data.
"""
from textwrap import dedent
import simplejson

iiif_info = {
    'profile': [
        'http://iiif.io/api/image/2/level1.json',
        {
            'supports': [
                'regionByPct', 'sizeByForcedWh', 'sizeByWh',
                'profileLinkHeader', 'jsonldMediaType'
            ],
            'qualities': ['color', 'gray'],
            'formats': ['png']
        }
    ],
    'tiles': [{'width': 1000, 'scaleFactors': [4], 'height': 1000}],
    'protocol': 'http://iiif.io/api/image',
    'height': 1080,
    'width': 1920,
    '@context': 'http://iiif.io/api/image/2/context.json',
    '@id': 'http://iiif-host.org/iiif/image'
}
