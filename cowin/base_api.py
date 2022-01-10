from typing import Union

import requests
from requests.exceptions import HTTPError

from cowin import bot
from cowin.config import Constants

class BaseApi:

    def _call_api(self, url) -> Union[HTTPError, dict]:
        response = requests.get(url, headers=Constants.headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            bot.send_message('-1001389138549', e)
            return e
        return response.json()