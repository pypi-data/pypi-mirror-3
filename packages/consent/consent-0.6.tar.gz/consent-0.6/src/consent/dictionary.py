"""
Dictionary of system attributes.

"""

import os
import sys
import dm.dictionary
import consent
import consent.dictionarywords
from consent.dictionarywords import *

class SystemDictionary(dm.dictionary.SystemDictionary):

    words = consent.dictionarywords

    def getSystemName(self):
        return 'consent'

    def getSystemTitle(self):
        return 'Consent'

    def getSystemServiceName(self):
        return 'Consent'

    def getSystemVersion(self):
        return consent.__version__

    def setDefaultWords(self):
        super(SystemDictionary, self).setDefaultWords()
        self[INITIAL_PERSON_ROLE] = 'Friend'
        self[MEMBER_ROLE_NAME] = 'Friend'
 
