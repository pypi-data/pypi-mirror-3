import sqlalchemy as sa
from sqlalchemy import orm

from fookebox.model import meta, schedule

def init_model(engine):
	"""Call me before using any of the tables or classes in the model."""

	#sm = orm.sessionmaker(autoflush=True, autocommit=True, bind=engine)
	sm = orm.sessionmaker(autoflush=True, autocommit=False, bind=engine)

	meta.engine = engine
	meta.Session = orm.scoped_session(sm)
