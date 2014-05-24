#!/usr/bin/env python3
#import urllib.parse, urllib2.request

import json
#import ijson

try:
    # py3
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
except ImportError:
    # py2
    from urllib2 import Request, urlopen
    from urllib import urlencode



class YQLQuery(object):
    def __init__(self, s):
        self.symbol = s
        self.params = {'symbol': s,}
        self.SETTINGS = {
                    'url': 'http://query.yahooapis.com/v1/public/yql',
                    'db_url': 'store://datatables.org/alltableswithkeys',
                    'stocks': 'yahoo.finance.quotes',
                    'option': 'yahoo.finance.options'
        }

    def get_stock(self, **kwargs):
        self.params = {'symbol': self.symbol,}
        self.__format_args(kwargs)
        columns = self.__format_column_list(self.params['columns'])
        yql = 'select {} from {} where symbol = \'{}\''.format( \
                                                                columns, self.SETTINGS['stocks'], self.params['symbol'])
        response = self.execute(yql)
        return self.__validate_response(response, 'quote')

    def get_option(self, **kwargs):
        self.params = {'symbol': self.symbol,}
        self.__format_args(kwargs)
        columns = self.__format_column_list(self.params['columns'])
        yql = 'select {} from {} where symbol = \'{}\''.format( \
                                                                columns, self.SETTINGS['option'], self.params['symbol'])
        if not 'exp' in self.params:
            raise SyntaxError("Expiration argument is required")
        yql += " and expiration='{}'".format(self.params['exp'])
        response = self.execute(yql)
        return self.__validate_response(response, 'optionsChain')

    def execute(self, yql):
        queryString = urlencode( \
                                 {'q': yql, 'format': 'json', 'env': self.SETTINGS['db_url']})
    
        url = self.SETTINGS['url']+'?'+queryString
        req = Request(url)
        resp = urlopen(req)
        return json.loads(bytes.decode(resp.read()))
        

    def __format_args(self,args):
        for k,v in args.items():
            if k not in self.params:
                self.params[k] = v
            if not 'columns' in self.params:
                self.params['columns'] = '*'

    def __format_column_list(self, columns):
        return ','.join([column for column in columns])

    def __is_valid_response(self, response, field):
        return 'query' in response and 'results' in response['query'] \
            and field in response['query']['results']

    def __validate_response(self, response, tagToCheck):
        if self.__is_valid_response(response, tagToCheck):
            quoteInfo = response['query']['results'][tagToCheck]
        else:
            if 'error' in response:
                raise QueryError(
                                 'YQL query failed with error: "{0}"'.format( \
                                                                              response['error']['description']))
            else:
                raise QueryError('YQL response malformed.')
        return quoteInfo

class QueryError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

