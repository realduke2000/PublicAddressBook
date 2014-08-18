#platform='sae'
platform=''
import os
import web
import shelve
import datetime
import threading
import atexit

if platform=='sae':
	import sae.const
	import MySQLdb as mdb

token_md5 = "e191efb684695f634db7004986c81487"
global auth_cache

app_root = os.path.dirname(__file__)
templates_root = os.path.join(app_root, 'templates')
render = web.template.render(templates_root)

class shelf_cache:
	def __init__(self,slef_path):
		self.__cache = shelve.open(slef_path)
		self.__cache.sync()

		for k in self.__cache.keys():
			cache_date = datetime.datetime.strptime(self.__cache[k][:10], "%Y-%m-%d")
			now_date = datetime.datetime.now()
			if (now_date - cache_date).days > 7:
				del self.__cache[k]
	
	def __del__(self):
		self.__cache.close()
	
	def has_key(self, k):
		if self.__cache.has_key(k):
			cache_date = datetime.datetime.strptime(self.__cache[k][:10], "%Y-%m-%d")
			now_date = datetime.datetime.now()
			if (now_date - cache_date).days > 7:# remove expired cache
				del self.__cache[k]
				return False
			else:
				return True
		else:
			return False

	def __getitem__(self, index):
		return self.__cache[index]

	def __setitem__(self, index, value):
		self.__cache[index] = value
	
	def __delitem__(self, index):
		del self.__cache[index]

class db_cache:
	def __init__(self):
		self.__conn = mdb.connect(charset='utf8', port=int(sae.const.MYSQL_PORT), host=sae.const.MYSQL_HOST, user=sae.const.MYSQL_USER, passwd=sae.const.MYSQL_PASS, db=sae.const.MYSQL_DB)
		self.__cursor = self.__conn.cursor()
		self.__cache={}
		
		self.__cursor.execute("select auth_cookie, cookie_set_time from auth_cache")
		results = self.__cursor.fetchall()
		if results is not None and len(results) > 0:
			for r in results:
				self.__cache[r[0]] = r[1]

	def __del__(self):
		self.__conn.close()

	def has_key(self, k):
		if self.__cache.has_key(k):
			cache_date = datetime.datetime.strptime(self.__cache[k][:10], "%Y-%m-%d")
			now_date = datetime.datetime.now()

			if (now_date - cache_date).days > 7 :
				del self.__cache[k]
				self.__cursor.execute("delete from auth_cache where auth_cookie=%s", (k,))
				self.__conn.commit()
				return False
			else:
				return True
		else:
			return False # Assume the cache in memory is the same as it in DB

	def __getitem__(self, k):
		return self.__cache[k]

	def __setitem__(self, k, v):
		if self.__cache.has_key(k):
			self.__cursor.execute("delete from auth_cache where auth_cookie=%s", (k,)) # update cache

		self.__cache[k] = v
		self.__cursor.execute('insert into auth_cache(auth_cookie, cookie_set_time) values(%s, %s)', (k, self.__cache[k],))
		self.__conn.commit()

	def __delitem__(self, k):
		del self.__cache[k]
		self.__cursor.execute('delete from auth_cache where auth_cookie=%s',(k,))
		self.__conn.commit()

if platform=='sae':
	auth_cache = db_cache()
else:
	auth_cache = shelf_cache(os.path.join(app_root, 'shelf'))

def has_loggedin():
	auth_token = web.cookies().get('auth')
	if auth_token and auth_cache.has_key(auth_token):
		return True
	else:
		return False
