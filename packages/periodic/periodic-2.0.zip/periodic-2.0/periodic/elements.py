#!/usr/bin/env python

import element_data

#invatomicmass = { 1.0079: 'H'}
#inv_pro = {1:'H'}
#symbols = {'krypton':'Kr'}
#elements = {'Os' : {'mass': 190.2 , 'name' : 'osmium' , 'atomic' : 76 , 'alt' : 'os',  'charge' : (3, 4), 'type': 'metal'} ,
ideas = '''
base class for elements
error class for not found elements
'''

DEBUG = False

def __converter__(element):
    
    try:
        for each in element_data.elements:
            if float(element) == element_data.elements[each]['mass']:
                return float(element)
    except ValueError:    pass
    
    try:
        for each in element_data.elements:
            if int(element) == element_data.elements[each]['atomic']:
                return int(element)
    except ValueError:    pass
    
    try:
        for each in element_data.elements:
            if element == element_data.elements[each]['name']:
                return element
    except ValueError:    pass
    
    try:
        if element.capitalize() in element_data.elements:
            return element.capitalize()
    except KeyError:    pass

def find(element):
    """Takes atomic mass (float only), atomic number (integer or string), symbol, or abbreviation
    of an element.

    Returns the element's capitalized symbol, for use by the `Element class <#elements.Element>`_.

    >>> find('h')
    'H'
    >>> find(12)
    'Mg'
    >>> find('boron')
    'B'
    >>> find('12')
    'Mg'
    """
    original_input = element
    element = __converter__(element)
    if type(element) == int:
        return element_data.inv_pro[element]
    if type(element) == float:
        return element_data.invatomicmass[element]
    if type(element) == str:
        if len(element) <= 2 and element_data.elements[element]:
            return element
        if len(element) > 2:
            return element_data.symbols[element]
    else:
        print "Error: '%s' not found" % original_input

#elements = {'Os' : {'mass': 190.2 , 'name' : 'osmium' , 'atomic' : 76 , 'alt' : 'os',  'charge' : (3, 4), 'type': 'metal'} ,

def get(element):
    """Takes input identical to the `element class <#periodic.element>`_.

    Returns a dictionary of information on the queried element.

    >>> import periodic
    >>> from pprint import pprint
    >>> magnesium = periodic.get(12) #'12','mg','Mg','magnesium','Magnesium', and 24.305 would have all worked just as well
    >>> pprint(magnesium) #This just looks nicer
    {'alt': 'mg',
     'atomic': 12,
     'charge': 2,
     'mass': 24.305,
     'name': 'magnesium',
     'type': 'metal'}
    """
    symbol = find(element)
    return element_data.elements[symbol]

class element(object):
    """
    **Parameters**

    The input for element [#element]_ can be any of the following, and is case *insensitive*.

    * element name (example: hydrogen) - **STRING**
    * element symbol (example: H) - **STRING**
    * atomic number (example: 1) - **INTEGER** [#semantic]_
    * atomic mass  (example: 1.0079) - **FLOAT**

    **Attributes**
    
    * symbol
    * name
    * mass
    * atomic
    * charge
    * type

    >>> import periodic
    >>> osmium = periodic.element('Os') #Here we create the element object. The input could have been any of the above types of input.
    >>> osmium.name
    'osmium'
    >>> osmium.symbol
    'Os'
    >>> osmium.atomic
    76
    >>> osmium.charge #These come in tuples of integers or lone integers
    (3, 4)
    >>> osmium.type
    'metal'
    """
    def __init__(self,symbol):
        self.symbol = find(symbol)
        self.element = element_data.elements[self.symbol]
        self.name = self.element['name']
        self.mass = self.element['mass']
        self.atomic = self.element['atomic']
        self.charge = self.element['charge']
        self.type = self.element['type']


if DEBUG:
    import doctest
    doctest.testmod()
