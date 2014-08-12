import web,os,re
import globals
from web import form
from globals import auth_cache, render

if globals.platform=='sae':
	import sae_model as model
	from sae_model import contact_data
else:
	import model
	from model import contact_data

urls = (
	"/", "contact",
	"/del/(\d+)",'delete_contact',
	"/vcf/(\d+|all)\.vcf",'contact_vcf',
)

class contact:
	contact_form = form.Form(
			form.Hidden("Contact_Id", description="contact_id"), 
			form.Textbox("Name", form.notnull, description="name"),
			form.Textbox("Telephone1", description="telephone1"),
			form.Textbox("Telephone2", description="telephone2"),
			form.Textbox("Location", description="location"),
			form.Textbox("Industry", description="industry")
		)
	def GET(self):
		f = contact.contact_form()
		if globals.has_loggedin():
			# render contact data
			data = model.get_all_contact()
			return render.contact(f, data)
		else:
			raise web.seeother("/",True)

	def POST(self):
		'''
		Add a new contact
		'''

		if not globals.has_loggedin():
			raise web.seeother("/contact/", True)

		f = contact.contact_form()
		if not f.validates():
			raise web.seeother('/contact/', True)

		data = contact_data(f['Contact_Id'].value, f['Name'].value, f['Telephone1'].value, f['Telephone2'].value, f['Location'].value, f['Industry'].value)
	
		# if this contact has been in db, del/new as update it
		#if model.get_contact(data.id) is not None:
		#	model.del_contact(data.id)

		model.new_contact(data)
		web.seeother("/contact/", True)

class delete_contact:
	def POST(self, id):
		if globals.has_loggedin():
			model.del_contact(id)

		raise web.seeother('/contact/', True)

class contact_vcf:
	def GET(self, id):
		if globals.has_loggedin():
			web.header('Contect-Type', 'text/x-vcard;charset=utf-8')
			web.header("Content-Disposition", 'attachment')

			if id=='all':
				all_data = model.get_all_contact()
				vcfs = ''
				for d in all_data:
					vcfs = vcfs + d.toVcard()

				if vcfs is not None and vcfs!= '':
					return vcfs
			elif re.match('^(\d+)$', id) is not None:
				id_raw = re.findall('\d+', id)
				if id_raw is not None and len(id_raw) > 0:
					id_raw = id_raw[0]
				data = model.get_contact(id_raw)
				if data is not None and data != '':
					return data.toVcard()
			else:
				print("id error, id=" + id);
				raise web.seeother('/contact/', True)
		else:
			raise web.seeother('/', True)

app_contact = web.application(urls, locals())

