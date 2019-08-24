import psycopg2
from conf.settings import databaseToken

class DatabaseConnection():
	def __init__(self):
		try:
			self.DATABASE_URL = databaseToken
			self.conn = psycopg2.connect(self.DATABASE_URL, sslmode='require')
			self.conn.autocommit = True
			self.cursor = self.conn.cursor()
		except:
			print('Não foi possível conectar ao database')

	async def query(self, ctx):
		self.cursor.execute(ctx)

	async def queryRegistro(self, ctx):
		self.cursor.execute(ctx)
		return self.cursor.fetchone()[0]

	async def queryAll(self, ctx):
		self.cursor.execute(ctx)
		return self.cursor.fetchall()