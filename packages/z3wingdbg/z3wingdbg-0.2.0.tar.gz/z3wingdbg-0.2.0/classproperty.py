"""Class Properties

:Author:   Philipp von Weitershausen
:Email:    philikon@philikon.de
:License:  Zope Public License, v2.1
:URL:      http://codespeak.net/svn/user/philikon/classproperty/

"""

__docformat__ = 'restructuredtext'

class classpropertytype(property):

    def __init__(self, name, bases=(), members={}):
        return super(classpropertytype, self).__init__(
            members.get('__get__'),
            members.get('__set__'),
            members.get('__delete__'),
            members.get('__doc__')
            )

classproperty = classpropertytype('classproperty')
