import json
import urllib2, urllib
import re

class Converter:
    """ A currency converter class """
    def __init__(self,amount,from_cur,to_cur):
        self.amount = amount
        self.from_cur = from_cur
        self.to_cur = to_cur
        self.query = {'amount':self.amount, 
         'from':self.from_cur,
         'to' :self.to_cur,
         'eq':'%3D%3F'} # the %3D%3F is equivalent to ?=
        self.url = "http://www.google.com/ig/calculator?hl=en&q=%(amount)s%(from)s%(eq)s%(to)s" % self.query
        self._ratio = self.generate_ratio()

    def ratio(self):
        return self._ratio

    def generate_ratio(self):
        self.query = {'amount':self.amount, 
         'from':self.from_cur,
         'to' :self.to_cur,
         'eq':'%3D%3F'} # the %3D%3F is equivalent to ?=
        self.url = "http://www.google.com/ig/calculator?hl=en&q=%(amount)s%(from)s%(eq)s%(to)s" % self.query

        converter = urllib2.urlopen(self.url)
        raw_data = converter.read()
        j = self.sanitize(raw_data)
        data = json.loads(j)
        lhs = data['lhs'].split(" ")[0]
        rhs = data['rhs'].split(" ")[0]
        cur_ratio = {'from':lhs,'to':rhs}
        self._ratio = cur_ratio

        return cur_ratio

    def result(self):

        return self._ratio['to']

    def sanitize(self,raw_data):
        """ cleans up json that doesn't use double quotes 
           for its keys """
        j = raw_data
	# The json returned from this service is badly formatted
        # json.loads expects well formed json
        # with keys that have double quotes
        # e.g. {"good":"json","uses":"doublequotes"}
	# The regular expressions 
        # below are used to clean up the
	# returned object and make it proper json
	# borrowed from http://stackoverflow.com/questions/4033633/handling-lazy-json-in-python-expecting-property-name

	j = re.sub(r"{\s*(\w)", r'{"\1', j)
	j = re.sub(r",\s*(\w)", r',"\1', j)
	j = re.sub(r"(\w):", r'\1":', j)
        return j
      


