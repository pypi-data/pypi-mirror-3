import sqlalchemy as sa

from sqlalchemybwc import db
from sqlalchemybwc.lib.declarative import declarative_base, DefaultMixin
from sqlalchemybwc.lib.decorators import ignore_unique, transaction

Base = declarative_base()

class Radio(Base, DefaultMixin):
    __tablename__ = 'sabwp_radios'

    make = sa.Column(sa.Unicode(255), nullable=False)
    model = sa.Column(sa.Unicode(255), nullable=False)
    year = sa.Column(sa.Integer, nullable=False)

class Car(Base, DefaultMixin):
    __tablename__ = 'sabwp_cars'

    make = sa.Column(sa.Unicode(255), nullable=False)
    model = sa.Column(sa.Unicode(255), nullable=False)
    year = sa.Column(sa.Integer, nullable=False)

    radio_id = sa.Column(sa.Integer, sa.ForeignKey(Radio.id), nullable=False)
    radio = sa.orm.relation(Radio, lazy=False)

    def __repr__(self):
        return '<Car %s, %s, %s>' % (self.make, self.model, self.year)
