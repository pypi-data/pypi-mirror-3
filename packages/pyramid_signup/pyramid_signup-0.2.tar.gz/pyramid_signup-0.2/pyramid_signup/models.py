from pyramid.i18n import TranslationStringFactory
from pyramid.security import Allow

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy.types import Integer
from sqlalchemy.types import UnicodeText
from sqlalchemy.types import Boolean
from sqlalchemy.types import DateTime
from sqlalchemy.orm import synonym
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr

import cryptacular.bcrypt
import re

from datetime import datetime
from datetime import timedelta
from datetime import date

from pyramid_signup.lib import gen_hash_key

_ = TranslationStringFactory('pyramid_signup')

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

class SUBase(object):
    """Base class which auto-generates tablename, and surrogate
    primary key column.
    """
    __table_args__ = {"sqlite_autoincrement": True}

    @declared_attr
    def __tablename__(cls):
        """Convert CamelCase class name to underscores_between_words 
        table name."""
        name = cls.__name__
        return (
            name[0].lower() + 
            re.sub(r'([A-Z])', lambda m:"_" + m.group(0).lower(), name[1:])
        )

    pk =  Column(Integer, primary_key=True)

    def serialize(self):
        """Converts all the properties of the object into a dict
        for use in json
        """
        props = {}

        for key in self.__dict__:
            if not key.startswith('__') and not key.startswith('_sa_'):
                obj = getattr(self, key)

                if isinstance(obj, datetime) or isinstance(obj, date):
                        props[key] = obj.isoformat()
                else:
                    props[key] = getattr(self, key)

        return props

SUEntity = declarative_base(cls=SUBase)

org_member_table = Table('organization_member', SUEntity.metadata,
    Column('user_pk', Integer(),
        ForeignKey('user.pk', onupdate='CASCADE', ondelete='CASCADE')
    ),

    Column('org_pk', Integer(),
        ForeignKey('organization.pk', onupdate='CASCADE', ondelete='CASCADE')
    )
)

class Activation(SUEntity):
    """
    Handle activations/password reset items for users

    The code should be a random hash that is valid only one time
    After that hash is used to access the site it'll be removed

    The created by is a system: new user registration, password reset, forgot
    password, etc.

    """
    code = Column(UnicodeText)
    valid_until = Column(DateTime)
    created_by = Column('created_by', UnicodeText)

    def __init__(self, created_system=None, valid_until=None):
        """ Create a new activation, valid_length is in days """
        self.code =  gen_hash_key(12)
        self.created_by = created_system

        if valid_until:
            self.valid_until = valid_until
        else:
             self.valid_until = datetime.utcnow() + timedelta(days=3)

class Organization(SUEntity):
    """ Represents an organization a user can be attached to """
    name = Column(UnicodeText, unique=True, nullable=False)
    create_date = Column(DateTime, default=datetime.utcnow)
    suspended = Column(Boolean, default=False)
    suspended_on = Column(DateTime)
    suspended_reason = Column(UnicodeText, nullable=True)
    cancelled = Column(Boolean, default=False)
    cancelled_on = Column(DateTime)
    cancelled_reason = Column(UnicodeText, nullable=True)
    owner_pk = Column(Integer, ForeignKey('user.pk'))
    owner = relation('User', backref='owned_organizations')
    users = relation('User', secondary=org_member_table, backref='organizations')

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.users.append(owner)

    @property
    def __acl__(self):
        """ Give access to the access_organization permission if they 
            are part of the organization
        """
        return [
                (Allow, 'organization:%s' % self.pk, 'access_organization')
        ]


group_member_table = Table('usergroupmember', SUEntity.metadata,
    Column('user_id', Integer(),
        ForeignKey('user.pk', onupdate='CASCADE', ondelete='CASCADE')
    ),

    Column('group_id', Integer(),
        ForeignKey('user_group.pk', onupdate='CASCADE', ondelete='CASCADE')
    )
)

class UserGroup(SUEntity):
    name = Column(UnicodeText, unique=True)
    description = Column(UnicodeText)

    users = relation('User', secondary=group_member_table, backref='groups')

    def __init__(self, name, desc):
        self.name = name
        self.description = desc

class User(SUEntity):
    username = Column(UnicodeText, unique=True)
    email = Column(UnicodeText, nullable=True)
    first_name = Column(UnicodeText)
    last_name = Column(UnicodeText)
    activated = Column(Boolean, default=False)
    activation_pk = Column(Integer, ForeignKey('activation.pk'))
    activation = relation('Activation', backref='user')
    suspended = Column(Boolean, default=False)
    suspended_on = Column(DateTime)
    suspended_reason = Column(UnicodeText, nullable=True)
    cancelled = Column(Boolean, default=False)
    cancelled_on = Column(DateTime)
    cancelled_reason = Column(UnicodeText, nullable=True)
    salt = Column(UnicodeText)

    _password = Column('password', UnicodeText)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = self.hash_password(password)

    def hash_password(self, password):
        if not self.salt:
            self.salt = gen_hash_key(24)

        return unicode(crypt.encode(password + self.salt))

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    @property
    def display_name(self):
        if self.first_name and self.last_name:
            return '%s %s' % (self.first_name, self.last_name)
        else:
            return self.username

    @property
    def __acl__(self):
        return [
                (Allow, 'user:%s' % self.pk, 'access_user')
        ]

