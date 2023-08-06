import unittest

from sqlalchemy import func

import amalgam


def make_models(db):
    Base = db('my')

    class Test(db.Base):
        name = db.String(50)
        pubdate = db.DateTime(default=func.now())

        class Meta:
            tablename = 'some'
            order_by = lambda: Test.name


    class Another(Base):
        title = db.String(50)
        test = db.ForeignKey(Test, backref='anothers')
        owner = db.ForeignKey(Test, backref='owned', nullable=True)


    class Container(Base):
        data = db.Serialized()

    return Test, Another, Container


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.db = amalgam.amalgam('sqla', 'sqlite://')
        self.Test, self.Another, self.Container = make_models(self.db)

        self.db.create_all()

    def tearDown(self):
        self.db.drop_all()

    def test_tablenames(self):
        self.assertEquals(self.Test.__tablename__, 'some')
        self.assertEquals(self.Another.__tablename__, 'my_another')

    def test_insert(self):
        t = self.Test(name=u'test')
        t.save()
        self.db.session.commit()

        t = self.Test.query.first()
        self.assertEquals(t.name, u'test')
        assert t.pubdate

    def test_fk(self):
        t = self.Test(name=u'test')
        a = self.Another(title=u'quest', test=t)
        t.save()
        a.save()
        self.db.session.commit()

        self.assertEquals(self.Another.query.first().test.id, t.id)
        self.assertEquals(self.Test.query.first().anothers[0], a)

    def test_serialized(self):
        t = self.Container(data={1: '1', '2': 2})
        t.save()
        self.db.session.commit()

        t = self.Container.query.first()
        self.assertEquals(t.data[1], '1')
        self.assertEquals(t.data['2'], 2)

    def test_default_ordering(self):
        t1 = self.Test(name=u'zxclater')
        t1.save()
        self.db.session.commit()

        t2 = self.Test(name=u'asdearlier')
        t2.save()
        self.db.session.commit()

        ts = self.Test.query.all()
        assert ts[0] == t2 and ts[1] == t1
