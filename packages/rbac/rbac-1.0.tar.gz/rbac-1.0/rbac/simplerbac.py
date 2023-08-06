#  simplerbac.py
#  
#  Copyright 2012 ahmed youssef <xmonader@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


  
ROLE,TASK,OPERATION=range(3)



class IAuthManager(object):
	
	def __init__(self):
		pass
		
	def _create_authitem(self, name, desc='', itemtype=OPERATION):
		pass
		
	def create_role(name, desc=''):
		self._create_authitem(self, name, desc, ROLE)
		
	def create_task(name, desc=''):
		self._create_authitem(self, name, desc, TASK)
		
	def create_operation(name, desc=''):
		self._create_authitem(self, name, desc, OPERATION)
		
	def item_by_name(self, item):
		pass
		
	def roles(self):
		pass
		
	def tasks(self):
		pass
		
	def operations(self):
		pass
		
	def add_child(self, item, child):
		pass
		
	def add_childs(self, item, kids):
		pass
	
	
	def init_from_ini(self, fp):
		import ConfigParser
		parser=ConfigParser.RawConfigParser(allow_no_value=True)
		parser.readfp(fp)
		authitemslist=parser.items("authitems") #(name, type)
		authitems={}
		#print self.parser.sections()
		for authitem, t in authitemslist:
			name=authitem
			_type=globals()[t.upper()]
			_desc=''
			if parser.has_section(authitem):
				if parser.has_option(authitem, "description"):
					_desc=parser.get(authitem, "description")
			self._create_authitem(name, _desc, _type)

		for authitem, t in authitemslist: #set childs
			if parser.has_section(authitem):
				if parser.has_option(authitem, "childs"):
					childs=parser.get(authitem, "childs")
					childs=childs.split()
					self.add_childs(authitem, childs)
		
		#now handle users assignments
		ua=parser.items("users")
		for uid, s in ua:
			whatlist=s.split()			
			self.assignmany(int(uid), whatlist)

	def init_from_json(self, jsonstr): #FIXME: fp?
		import json
		conf=json.loads(jsonstr)
		authitems=conf['acl']['items']
		for authitem in authitems:
			name=authitem
			_type=OPERATION
			_desc=''
			if authitem in conf['acl']: #has a key
				item=conf['acl'][authitem]

				if 'description' in item:
					_desc=item['description']
				if 'type' in item:
					_type=globals()[item['type'].upper()]

			self._create_authitem(name, _desc, _type)
			
		#now set childs
		for authitem in authitems:
			childs=None
			if authitem in conf['acl']:
				item=conf['acl'][authitem]
				if 'childs' in item:
					childs=item['childs']
					self.add_childs(authitem, childs)
				
		#now users
		users=conf['acl']['users']
		for u, lst in users.items():
			self.assignmany(int(u), lst)
			
class SimpleAuthItem(object):
	
	def __init__(self, name, desc='', itemtype=ROLE):
		self.name=name
		self.desc=desc
		self.itemtype=itemtype
		
		self.childs=[]
		
	def add_child(self, item):
		self.childs.append(item)
		
	def add_childs(self, kids):
		self.childs.extend(kids)
		
	def can(self, name):
		if self.name==name:
			return True
		else:
			for child in self.childs:
				if child.can(name):
					return True
		return False
		
	def __str__(self):
		lookup={0:'Role', 1:'Task', 2:'Operation'}
		return self.name+ " isA "+lookup[self.itemtype]+ " ==> "+ self.desc
	
	def print_me(self):
		print self.name

		for child in self.childs:
			child.print_me()

	
class SimpleAuthManager(IAuthManager):
	
	def __init__(self):
		self.authitems=[]
		self._assignments={} # {id: [manyitems] }
	
	def _create_authitem(self, name, desc='', itemtype=OPERATION):
		self.authitems.append(SimpleAuthItem(name, desc, itemtype))
		
	def create_role(self, name, desc=''):
		self._create_authitem(name, desc, ROLE)
		
	def create_task(self, name, desc=''):
		self._create_authitem(name, desc, TASK)
		
	def create_operation(self, name, desc=''):
		self._create_authitem(name, desc, OPERATION)
		
	def roles(self):
		return [item for item in self.authitems if item.itemtype==ROLE]
		
	def tasks(self):
		return [item for item in self.authitems if item.itemtype==TASK]
		
	def operations(self):
		return [item for item in self.authitems if item.itemtype==OPERATION]
		
	def item_by_name(self, name):
		for item in self.authitems:
			if item.name==name:
				return item
		raise ValueError
				
	def add_child(self, item1name, item2name):
		item1=self.item_by_name(item1name)
		item2=self.item_by_name(item2name)
		
		item1.add_child(item2)
		
	def add_childs(self, item1name, itemsnames):
		item1=self.item_by_name(item1name)
		for item in itemsnames:
			item1.add_child(self.item_by_name(item))
	
	def can(self, name, what):
		item=self.item_by_name(name)
		return item.can(what)
		
		
	def assign(self, uid, what):
		if self._assignments.has_key(uid):
			self._assignments[uid].append(what)
		else:
			self._assignments[uid]=[what]
			
	def assignmany(self, uid, whatlist):

		if self._assignments.has_key(uid):
			self._assignments[uid].extend(whatlist)
		else:
			self._assignments[uid]=whatlist
		
	def user_can(self, uid, what):
		if self._assignments.has_key(uid):
			itemsnames=self._assignments[uid]
			#directly 
			if what in itemsnames:
				return True
			#otherwise check every item it maybe in its childs
			for itemname in itemsnames:
				if self.item_by_name(itemname).can(what):
					return True

		return False
		

			
		
	def get_user_caps(self, uid):
		return self._assignments.get(uid, None)
		
	def print_me(self):
		for x in self.authitems:
			x.print_me()
	

			
	
def testJSON():

	
	s="""
	

{
	"acl":{

		"items":["admin","user","taskmanagement", "topic.create", "topic.delete", "topic.read", "topic.update"],
		"admin":{
			"type":"role",
			"description":"admin role",
			"childs":["taskmanagement"]
		},
		"user":{
			"type":"role",
			"description":"user role",
			"childs":["topic.create", "topic.read", "topic.update"]
		},
		"taskmanagement":{
			"type":"task",
			"description":"topic crud",
			"childs":["topic.create", "topic.delete", "topic.read", "topic.update"]
		},
		"topic.create":{
			"type":"operation",
			"description":"topic.create operation"
		},
		"users":{
			"1":["user", "topic.delete"],
			"2":["user"]
		}

	}
}
"""

	sm=SimpleAuthManager()
	sm.init_from_json(s)
	print sm.get_user_caps(1)
	print "admin can topic.delete", sm.can("admin", "topic.delete")
	print "user can topic.delete", sm.can("user", "topic.delete")
	print "user 1 can topic.delete", sm.user_can(1, "topic.delete")
	print "user 2 can topic.delete", sm.user_can(2, "topic.delete")
	
	adm=sm.item_by_name("admin")



	
def testSimpleAuthManager():
	sm=SimpleAuthManager()
	sm.create_role("user", "user role")
	sm.create_operation("topic.create", "creating topics")
	sm.create_operation("topic.read", "reading topics")
	sm.create_operation("topic.update", "updating topics")
	sm.create_operation("topic.delete", "deleting topics")
	sm.create_task("topicManagement", "crud")
	sm.add_childs("topicManagement", ["topic.create", "topic.read", "topic.update", "topic.delete"])
	sm.add_childs("user", ["topic.create", "topic.read", "topic.update"])
	print "user can topic.read", sm.can("user", "topic.read")
	print "user can topic.delete", sm.can("user", "topic.delete")
	
	sm.create_role("admin", "admin role")
	sm.add_child("admin", "topicManagement")
	u=sm.item_by_name("user")
	u.print_me()
	
	print "*" * 30
	a=sm.item_by_name("admin")
	a.print_me()
	print "a can topic.create", sm.can("admin", "topic.create")
	print "a can topic.delete", sm.can("admin", "topic.delete")
	
	
	ahmed_id=1
	sm.assign(ahmed_id, "user")
	sm.assign(ahmed_id, "topicManagement")
	print "ahmed can topic.create", sm.user_can(ahmed_id, "topic.create")
	print "ahmed can topic.delete", sm.user_can(ahmed_id, "topic.delete")
	

def testINI():
	import io
	
	
	s="""
[authitems]
admin=role
taskmanagement=task
user=role
topic.create=operation
topic.read=operation
topic.update=operation
topic.delete=operation


[taskmanagement]
childs=topic.read topic.create topic.read topic.update topic.delete
description= topic crud task

[admin]
childs=taskmanagement
description=admin role

[user]
childs=topic.read topic.create





[topic.create]
description=create topic 

[users]
1=user topic.delete
2=user

""" 
	fp=io.BytesIO(s)
	
	sm=SimpleAuthManager()
	sm.init_from_ini(fp)
	print sm.get_user_caps(1)
	print "admin can topic.delete", sm.can("admin", "topic.delete")
	print "user can topic.delete", sm.can("user", "topic.delete")
	print "user 1 can topic.delete", sm.user_can(1, "topic.delete")
	print "user 2 can topic.delete", sm.user_can(2, "topic.delete")
	

if __name__=="__main__":
	#testINI() 
	#testSimpleAuthManager()
	testJSON()
		





