import web

import login
import contact

urls = (
	'/contact', contact.app_contact,
	'/', login.app_login,
)

def notfound():
	raise web.seeother('/', True)

app_main = web.application(urls, locals())
app_main.notfound = notfound

if __name__=='__main__':
	dir(app_main)
	app_main.run()
