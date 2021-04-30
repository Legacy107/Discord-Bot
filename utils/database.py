import asyncio
from dotenv import load_dotenv, find_dotenv
import os

from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

# Load config from env
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
DATABASE_URL = os.getenv('DATABASE_URL')

Base = declarative_base()


class Pic(Base):
	__tablename__ = 'pic'

	id = Column(String, primary_key=True)
	url = Column(String)
	name = Column(String)

	# required in order to access columns with server defaults
	# or SQL expression defaults, subsequent to a flush, without
	# triggering an expired load
	__mapper_args__ = {'eager_defaults': True}


class PicDatabase:
	def __init__(self):
		self.engine = None
		self.async_sessionmaker = None

	async def setup(self):
		self.engine = create_async_engine(
			DATABASE_URL,
			poolclass=NullPool,
			future=True
		)

		async with self.engine.begin() as conn:
			# await conn.run_sync(Base.metadata.drop_all)
			await conn.run_sync(Base.metadata.create_all)

		# expire_on_commit=False will prevent attributes from being expired
		# after commit.
		self.async_session = sessionmaker(
			self.engine,
			expire_on_commit=False,
			class_=AsyncSession
		)

	async def add_pic(self, id, url, name):
		async with self.async_session() as session:
			async with session.begin():
				session.add(Pic(id=id, url=url, name=name))

	async def delete_pic(self, id):
		async with self.async_session() as session:
			async with session.begin():
				pic = await session.get(Pic, id)
				await session.delete(pic)

	async def get_all_pics(self):
		async with self.async_session() as session:
			async with session.begin():
				pics = await session.execute(select(Pic).order_by(Pic.id))
				# print(pics.scalars().all())
				return [{'id': pic.id, 'url': pic.url, 'name': pic.name} for pic in pics.scalars()]

	async def get_pic_url(self, id):
		async with self.async_session() as session:
			async with session.begin():
				pic = await session.get(Pic, id)
				return pic.url

	async def has_pic(self, id):
		async with self.async_session() as session:
			async with session.begin():
				pic = await session.get(Pic, id)
				return bool(pic)


async def _test():
	db_client = PicDatabase()
	await db_client.setup()
	await db_client.add_pic('abd', 'abd', 'abd')
	await db_client.add_pic('abc', 'abc', 'abc')
	print(await db_client.has_pic('abd'))
	print(await db_client.get_all_pics())
	await db_client.delete_pic('abc')
	print(await db_client.has_pic('abc'))

if __name__ == '__main__':
	asyncio.run(_test())
