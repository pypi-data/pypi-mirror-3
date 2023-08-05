################################################################
# vs.event - published under the GPL 2
# Authors: Andreas Jung, Veit Schiele, Anne Walther
################################################################

import re
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator
from Products.validation.validators.RegexValidator import RegexValidator
from zope.interface import implements

class VSLinesOfDateValidator:
    implements(IValidator)

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description
        self.re_line = re.compile('^\d{4}-\d{2}-\d{2}$')

    def __call__(self, value, *args, **kwargs):
        error_msg = ""
        for val in value:
            if not self.re_line.match(val):
                error_msg = "invalid date-string"

        if error_msg:
            return error_msg
        else:
            return True

validators = [
    RegexValidator(
        'isLineOfInts',
        r'^$|-?\d+(,-?\d+)*$',
        title='',
        description='',
        errmsg='',
    ),
    VSLinesOfDateValidator(
        'linesOfDates', title="Validator for Date-Strings",
        description=""
    ),
]

for validator in validators:
    validation.register(validator)
