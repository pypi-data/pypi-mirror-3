import unittest

from sqlalchemy import func

import amalgam


def make_models(db):
    Base = db('test')

    class Person(Base):
        name = db.String(50)

    class Group(Base):
        name = db.String(50)
        members = db.ManyToMany(Person, backref='groups')#, through='Membership')

    # FIXME: no idea how to test `through` in such environment - it's
    # impossible to reference Membership as class directly or by path
    class Membership(Base):
        person = db.ForeignKey(Person)
        group = db.ForeignKey(Group)
        joined = db.Date(default=func.now())

    return Person, Group, Membership


class M2MTest(unittest.TestCase):
    def setUp(self):
        self.db = amalgam.amalgam('sqla', 'sqlite://')
        self.Person, self.Group, self.Membership = make_models(self.db)

        self.db.create_all()

    def tearDown(self):
        self.db.drop_all()

    def test_m2m(self):
        p = self.Person(name=u'Bogdan')
        p.save()
        g = self.Group(name=u'Getmans', members=[p])
        g.save()

        self.db.session.commit()

        self.assertEquals(self.Group.query.first().members[0], p)
        self.assertEquals(self.Person.query.first().groups[0], g)
