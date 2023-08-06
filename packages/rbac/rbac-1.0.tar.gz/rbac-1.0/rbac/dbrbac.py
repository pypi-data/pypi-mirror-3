#  dbrbac.py
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

from sqlalchemy import create_engine, ForeignKey, Column, Integer, String
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from simplerbac import *

Base = declarative_base()

sess=None
def set_db(to='sqlite:///:memory:', create=False, echo=False):
	"""used to set the path of the database
	create: creating table 
	echo  : show sql statements executed
	"""
	global sess
	
	engine=create_engine(to, echo=echo)
	Session=sessionmaker()
	Session.configure(bind=engine)
	sess=Session()
	
	if create is True:
		Base.metadata.create_all(engine)
	
#3 tables authitem(name, desc, type), authitemchild(itemid, childid), authitem_assignments (uid,  itemid)	
class AuthItem(Base):
	__tablename__='authitems'
	id=Column(Integer, primary_key=True)
	name=Column(String, unique=True)
	desc=Column(String)
	itemtype=Column(Integer) #ROLE,TASK,OPERATION
	childs = relationship("AuthItemChild")

	def __init__(self, name, desc='', itemtype=OPERATION):
		self.name=name
		self.desc=desc
		self.itemtype=itemtype

	def get_caps(self):
		print self.name
		for c in self.childs:
			print c.child_name
			
	@staticmethod
	def item_by_name(itemname):
		try:
			return sess.query(AuthItem).filter_by(name=itemname).one()	
		except:
			None	
	
	def can(self, what):
		if self.name==what:
			return True
		for c in self.childs:
			if c.child_name == what:
				return True
			#check in the childs of the childs
			citem=AuthItem.item_by_name(c.child_name)
			
			if citem and citem.can(what):
				return True
		return False
			
	def add_child(self, kid):
		c=AuthItemChild(self.name, kid.name)
		sess.add(c)
		sess.commit()
		
	def add_childs(self, kids):
		objs=[]
		for k in  kids:
			objs.append( AuthItemChild(self.name, k.name))
		sess.add_all(objs)
		sess.commit()
	def __repr__(self):
		return self.name

	def print_me(self):
		print self.name
		for c in self.childs:
			c.child_name
			
			
class AuthItemChild(Base):
	__tablename__="authitemchilds"
	id=Column(Integer, primary_key=True)
	authitem_name=Column(String, ForeignKey("authitems.name"))
	child_name=Column(String)

	def __init__(self, authitem_name, child_name):
		self.authitem_name=authitem_name
		self.child_name=child_name

class UserAuthAssignment(Base):
	__tablename__="userauthassignments"
	id=Column(Integer, primary_key=True)
	uid=Column(Integer)
	child_name=Column(String)
	
	def __init__(self, uid, child_name):
		self.uid=uid
		self.child_name=child_name


class DBAuthManager(IAuthManager):
		
	def item_by_name(self, name):
		return AuthItem.item_by_name(name)
		

	def _create_authitem(self, name, desc='', itemtype=OPERATION):
		i=AuthItem(name, desc, itemtype)
		sess.add(i)
		sess.commit()
		
	def create_role(self, name, desc=''):
		self._create_authitem(name, desc, ROLE)
		
	def create_task(self, name, desc=''):
		self._create_authitem(name, desc, TASK)
		
	def create_operation(self, name, desc=''):
		self._create_authitem(name, desc, OPERATION)
		
	def roles(self):
		return sess.query(AuthItem).filter_by(itemtype=ROLE)
		
	def tasks(self):
		return sess.query(AuthItem).filter_by(itemtype=TASK)
		
	def operations(self):
		return sess.query(AuthItem).filter_by(itemtype=OPERATION)
		
	def add_child(self, item, child):
		item=self.item_by_name(item)
		item.add_child(self.item_by_name(child))
		
		
	def add_childs(self, item, kids):
		item=self.item_by_name(item)
		kids=[self.item_by_name(x) for x in kids]
		item.add_childs(kids)
	
	def can(self, itemname, what):
		item=self.item_by_name(itemname)
		return item.can(what)
		
	def assign(self, uid, what):
		a=UserAuthAssignment(uid, what)
		sess.add(a)
		sess.commit()
		
	def assignmany(self, uid, whatlist):
		for what in whatlist:
			obj=UserAuthAssignment(uid, what)
			sess.add(obj)
		sess.commit()
		
		
	def user_can(self, uid,  what):
		uas=sess.query(UserAuthAssignment).filter_by(uid=uid).all()
		if uas:
			for ua in uas:
				if ua.child_name==what:
					return True
				item=self.item_by_name(ua.child_name)
				if item and item.can(what):
					return True
		return False
		
		
def test_up():
	
	da=DBAuthManager()

	da.create_role("admin")
	da.create_role("user")
	da.create_task("taskman")
	da.create_operation("topic.read")
	da.create_operation("topic.create")
	da.create_operation("topic.delete")
	
	da.add_child("admin", "taskman")
	da.add_childs("taskman", ["topic.read", "topic.create", "topic.delete"])
	da.add_childs("user", ["topic.read", "topic.create"])
	
	da.assign(1, 'taskman')
	da.assign(2, 'user')

def testDBManager():
	set_db('sqlite:///:memory:', create=True, echo=False)
	test_up()
	da=DBAuthManager()
	
	adm=da.item_by_name("admin")
	adm.get_caps()
	
	tm=da.item_by_name("taskman")
	tm.get_caps()
	
	user=da.item_by_name("user")
	user.get_caps()
	
	print "user1 can taskman: ", da.user_can(1, "taskman")
	print "user1 can admin", da.user_can(1, "admin")
	print "user1 can topic.delete", da.user_can(1, "topic.delete")
	
	print "user2 can taskman: ", da.user_can(2, "taskman")
	print "user2 can topic.create", da.user_can(2, "topic.create")
	print "user2 can admin", da.user_can(2, "admin")


			
	
def testDBJSON():

	
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
	set_db('sqlite:///:memory:', create=True, echo=False)
	sm=DBAuthManager()
	sm.init_from_json(s)
	print "admin can topic.delete", sm.can("admin", "topic.delete")
	print "user can topic.delete", sm.can("user", "topic.delete")
	print "user 1 can topic.delete", sm.user_can(1, "topic.delete")
	print "user 2 can topic.delete", sm.user_can(2, "topic.delete")
	
	adm=sm.item_by_name("admin")


if __name__=="__main__":
	testDBJSON()
	#testDBManager()
	

