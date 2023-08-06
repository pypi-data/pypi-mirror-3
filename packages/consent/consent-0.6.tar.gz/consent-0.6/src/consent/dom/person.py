import dm.dom.person
from dm.dom.stateful import *

class Person(dm.dom.person.Person):
    "Registered person."

    sites = AggregatesMany('Member', key='site', isEditable=False)

