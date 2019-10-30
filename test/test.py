import os, sys, json, unittest, logging, datetime
from uuid import uuid4

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, DATE, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))  # noqa

import sqlalchemy_aurora_data_api

logging.basicConfig(level=logging.INFO)
logging.getLogger("aurora_data_api").setLevel(logging.DEBUG)
logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)

Base = declarative_base()


class User(Base):
    __tablename__ = "sqlalchemy_aurora_data_api_test"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
    doc = Column(JSONB)
    uuid = Column(UUID)
    woke = Column(Boolean, nullable=True)
    nonesuch = Column(Boolean, nullable=True)
    birthday = Column(DATE)
    added = Column(TIMESTAMP)


class TestAuroraDataAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sqlalchemy_aurora_data_api.register_dialects()
        cls.db_name = os.environ.get("AURORA_DB_NAME", __name__)
        cls.engine = create_engine('postgresql+auroradataapi://:@/' + cls.db_name)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_execute(self):
        with self.engine.connect() as conn:
            for result in conn.execute("select * from pg_catalog.pg_tables"):
                print(result)

    def test_orm(self):
        uuid = uuid4()
        doc = {'foo': [1, 2, 3]}
        Base.metadata.create_all(self.engine)
        ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname', doc=doc, uuid=str(uuid), woke=True,
                       birthday=datetime.datetime.fromtimestamp(0), added=datetime.datetime.now())
        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.add(ed_user)
        self.assertEqual(session.query(User).filter_by(name='ed').first().name, "ed")
        session.commit()
        self.assertGreater(session.query(User).filter(User.name.like('%ed')).count(), 0)
        u = session.query(User).filter(User.name.like('%ed')).first()
        self.assertEqual(u.doc, doc)
        self.assertEqual(u.woke, True)
        self.assertEqual(u.nonesuch, None)


if __name__ == "__main__":
    unittest.main()