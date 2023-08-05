from data import Data

_url = 'http://demo.hastests.com'
_token = '213a37b1-c8a9-4dae-acab-67f0fd65149e'

class Account(object):

    def __init__(self, url=_url, token=_token):
        self.url, self.token = url, token

    def add_program(self, program):
        return Data(program, self)

