"""Interface for interacting with IIIF services.
"""

import requests
import validators


class IIFInterface(object):
    """
    Proxy class for interacting with IIIF services.
    """

    @staticmethod
    def get_info(iiif_base):
        """Gets the info.json fo the given IIIF base URL.

        :param iiif_base: The IIIF base URL
        :return: dict
        """
        url = "%s/info.json" % (iiif_base, )
        if not validators.url(url):
            raise ValueError(
                "Info URL '%s' constructed from '%s' is not valid!" % (
                    url, iiif_base
                )
            )
        resp = requests.get(url)
        resp_json = resp.json()
        return resp_json
