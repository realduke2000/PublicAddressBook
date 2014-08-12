import web, os, datetime, sae.const, MySQLdb as mdb
import globals

class contact_data:
	def __init__(self, id='', name='', tel1='', tel2='',loc='',industry='',lastupdate=''):
		self.id = id
		self.name = name
		self.telephone1 = tel1
		self.telephone2 = tel2
		self.location = loc
		self.industry = industry
		if lastupdate == '':
			self.lastupdate = str(datetime.datetime.now()) 
		else:
			self.lastupdate = lastupdate

	def totuple(self):
		return (self.name,self.telephone1,self.telephone2,self.location,self.industry,self.lastupdate)
	
	def toVcard(self):
		s = u'''BEGIN:VCARD
FN;CHARSET=UTF-8:{0}
TEL;TYPE=cell:{1}
'''.format(self.name, self.telephone1)

		if (self.telephone2 is not None) and (self.telephone2 != ''):
			s = s + u'TEL;TYPE=WORK:{0}\r\n'.format(self.telephone2)

		s = s + u'ORG;CHARSET=UTF-8:' + self.industry + '\r\n'
		s = s + u'ADR;TYPE=home;CHARSET=UTF-8:' + self.location + '\r\n'
		s = s + 'END:VCARD\r\n'

		return s

def get_all_contact():
	conn = mdb.connect(charset='utf8', port=int(sae.const.MYSQL_PORT), host=sae.const.MYSQL_HOST, user=sae.const.MYSQL_USER, passwd=sae.const.MYSQL_PASS, db=sae.const.MYSQL_DB)
	cursor = conn.cursor()

	data = []

	try:
		cursor.execute("select id, name, telephone1, telephone2, location, industry, lastupdate from contact")
		results = cursor.fetchall()
		
		for r in results:
			data.append(contact_data(r[0],r[1],r[2],r[3],r[4],r[5],r[6]))
	except Exception as e:
		print e

	conn.close()

	return data

def get_contact(id):
	if (id is None) or (id==''):
		return None
	conn = mdb.connect(charset='utf8',host=sae.const.MYSQL_HOST, user=sae.const.MYSQL_USER,passwd= sae.const.MYSQL_PASS, db=sae.const.MYSQL_DB,port=int(sae.const.MYSQL_PORT))
	cursor = conn.cursor()
	
	data = None

	try:
		cursor.execute("select id, name, telephone1, telephone2, location, industry, lastupdate from contact where id=%s", (id,))
		r = cursor.fetchone()
		if r:
			data = contact_data(r[0],r[1],r[2],r[3],r[4],r[5],r[6])
	except Exception as e:
		print e

	conn.close()
	return data

def new_contact(data):
	if data is None:
		return
	conn = mdb.connect(charset='utf8',port=int(sae.const.MYSQL_PORT),host=sae.const.MYSQL_HOST, user=sae.const.MYSQL_USER, passwd=sae.const.MYSQL_PASS, db=sae.const.MYSQL_DB)
	cursor = conn.cursor()

	result = False

	try:
		cursor.execute("insert into contact(name, telephone1, telephone2, location, industry, lastupdate) values(%s,%s,%s,%s,%s,%s)", (data.name, data.telephone1, data.telephone2, data.location, data.industry, data.lastupdate))
		conn.commit()
		result = True
	except Exception as e:
		print e
	conn.close()
	
	return result

def del_contact(contact_id):
	if (contact_id is None) or (contact_id == ''):
		return
	conn = mdb.connect(charset='utf8',port=int(sae.const.MYSQL_PORT), host=sae.const.MYSQL_HOST, user=sae.const.MYSQL_USER, passwd=sae.const.MYSQL_PASS, db=sae.const.MYSQL_DB)
	cursor = conn.cursor()

	result = False
	
	try:
		cursor.execute("delete from contact where id = %s", (contact_id,))
		conn.commit()
		result = True
	except Exception as e:
		raise e
		print e
	
	conn.close()
	return result
