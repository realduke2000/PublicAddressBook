import web
from web import form
import os
import hashlib
import datetime

import globals

from globals import token_md5, auth_cache, render

urls = (
	"", "login"
)

class login:
	
	login_form = form.Form(
	form.Password("token", form.notnull, description="Token")
	)

	def GET(self):
		# check auth status
		if globals.has_loggedin():
			raise web.seeother("/contact/",True)
		f = login.login_form()
		return render.login(f)
	
	def POST(self):
		f = login.login_form()
		
		if not f.validates():
			return render.login(f)

		token = f['token'].value
		try:
			if token and token_md5 == hashlib.md5(token).hexdigest():
				# set auth cookie
				encryption = hashlib.md5(web.ctx.host + token).hexdigest()
				web.setcookie('auth', encryption, 60*60*24*7,path='/') #cookie expired in one week
				auth_cache[encryption]=str(datetime.datetime.today()) # for clean up cache
				raise web.seeother('/contact/',True)	
			else:
				return render.login(f)
		except TypeError as ex:
			print ex

app_login = web.application(urls, locals())

