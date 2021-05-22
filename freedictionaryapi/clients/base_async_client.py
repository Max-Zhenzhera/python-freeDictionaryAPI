"""
Contains base asynchronous dictionary API client.

.. class:: BaseAsyncDictionaryApiClient(BaseDictionaryApiClientInterface)
"""

import abc
import logging
import typing

from .base_client_interface import BaseDictionaryApiClientInterface
from ..languages import LanguageCodes
from ..parsers import DictionaryApiParser
from ..types import Word


__all__ = ['BaseAsyncDictionaryApiClient']


logger = logging.getLogger(__name__)


class BaseAsyncDictionaryApiClient(BaseDictionaryApiClientInterface):
    """
    Implements base asynchronous dictionary API client.

    Abstract client that supposed to be inherited
    for ``async`` clients.
    """

    @abc.abstractmethod
    async def fetch_api_response(self, url: str) -> typing.Tuple[int, typing.Any]:
        """
        Fetch data of the API response.

        It is a abstract method that
        must implement:

            - **asynchronous** HTTP request to the API by given url
              (url that is generated by input params in invoked function);
            - Get status code of the API response;
            - Cast API response to python object with JSON decoding,
              apparently it is provided in all web libraries,
              need to do something like that:
              ::

                  response: ResponseType
                  json_response: Any = await response.json()

        The most important part is
        returning - method must return tuple of:

            1. integer code of the API response;
            2. python object loaded from API response with JSON decoding.

        So:

            - integer code of the API response will be analyzed
              and correspond error will be raised
              if API returned one (response is unsuccessful);
            - python object that expresses API response
              will be parsed, so all information will be available.

        Finally, it should look like (pseudo code below):
        ::

            # make request just with library
            response: ResponseType
            response = await weblib.get(url)
            response_status_code = response.status_code
            json_response = await response.json()

            data_to_return = (response_status_code, json_response)

            return data_to_return

        ::

            # or maybe use some client/session
            # that have been passed on initialization
            response: ResponseType
            async with self._client.get(url) as response:
                response_status_code = response.status_code
                json_response = await response.json()

            data_to_return = (response_status_code, json_response)

            return data_to_return

        If it is still any questions
        you can also see some examples
        or just implementations of ready to use clients.

        :param url: url that is generated by input params in invoked function
        :type url: :obj:`str`

        :return: tuple of:

            - response status code;
            - python object loaded from API response with JSON decoding.
        :rtype: :obj:`tuple[int, Any]`
        """

    async def fetch_json(self, word: str, language_code: typing.Optional[LanguageCodes] = None) -> typing.Any:
        """
        Fetch API json response that loaded in Python object (``await response.json()``).

        :param word: searched word
        :type word: :obj:`str`
        :param language_code: language of the searched word
        :type language_code: :obj:`Optional[LanguageCodes]`

        :return: JSON response (supposed to be :obj:`list` or :obj:`dict`)
        :rtype: :obj:`Any`

        :raise:
            :DictionaryApiError: when unsuccessful status code got of API request
        """

        url, language_code = self._generate_url(word, language_code)

        logger.info(f'Send request to API with word {word!r} and language code {language_code!r}. URL: {url!r}.')

        response_status_code, json_response = await self.fetch_api_response(url)

        # logging - handling of API errors (and raising them)
        analyzed_response = self._analyze_response(url, response_status_code, json_response)

        return analyzed_response

    async def fetch_parser(self, word: str, language_code: typing.Optional[LanguageCodes] = None
                           ) -> DictionaryApiParser:
        """
        Fetch dictionary API parser.

        :param word: searched word
        :type word: :obj:`str`
        :param language_code: language of the searched word (`word`)
        :type language_code: :obj:`Optional[LanguageCodes]`

        :return: dictionary API parser
        :rtype: :obj:`DictionaryApiParser`
        """

        json_response = await self.fetch_json(word, language_code)
        parser = DictionaryApiParser(json_response)

        return parser

    async def fetch_word(self, word: str, language_code: typing.Optional[LanguageCodes] = None) -> Word:
        """
        Fetch word - parsed object that has all word info.

        Shortcut for the :attr:`DictionaryApiParser.word`.

        :param word: searched word
        :type word: :obj:`str`
        :param language_code: language of the searched word
        :type language_code: :obj:`Optional[LanguageCodes]`

        :return: word (parsed object)
        :rtype: :obj:`Word`
        """

        parser = await self.fetch_parser(word, language_code)
        word = parser.word

        return word
