from Acquisition import Implicit, aq_parent
from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.Archetypes.Storage import AttributeStorage

from Products.validation.config import validation
from Products.validation.interfaces.IValidator import IValidator

from zope.interface import classImplements

EMAIL_4 = False
import sys
try:
    from email import message
    EMAIL_4 = True
except ImportError:
    sys._IMPORTING_EMAIL_BACKPORT = True
    try:
        import email_backport as email
        sys.modules['email'] = email
        EMAIL_4 = True
    except ImportError:
        EMAIL_4 = False

try:
    import email.utils
    parseaddr = email.utils.parseaddr
except ImportError:
    parseaddr = lambda x: x,x

class RFC822AddressFieldValidator(Implicit):
    " "

    __implements__ = (IValidator,)

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kw):
        schema = instance.Schema()
        value = value.strip()
        addresses = value.strip().split(',')
        invalid = []
        for address in addresses:
            name, address_ = parseaddr(address)
            if not '@' in address_:
                invalid.append(address)
        if invalid:
            return "Invalid email addresses: " + ','.join(invalid)
        return True

try:
    classImplements(RFC822AddressFieldValidator, IValidator)
except TypeError:
    # In Plone < 4
    pass

validation.register(RFC822AddressFieldValidator('rfc822AddressField',
    title='RFC822 address field validator',
    description="""Validates that field contains a correct address combination""")
)
