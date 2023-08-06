import os

from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from monitor.notifier import ConsoleNotifier

db_file = os.path.join(os.path.dirname(__file__), "inner_db")
db_connexion = 'sqlite:///%s' % db_file

Base = declarative_base()
engine = create_engine(db_connexion, echo=False)
Session = sessionmaker(bind=engine)


SCRIPTS_FOLDER = ("scripts/check_*py",)
