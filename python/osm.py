#!/usr/bin/env python

# classes for OSM data

from xml.sax.handler import ContentHandler

class OSMNode:
	"""Encapsulate an OSM node"""
	def __init__(self,id=0):
		self.NodeID = id
		self.Lon = 0.0
		self.Lat = 0.0
		self.Tags = {}
	
	def AddTag(self,Key,Val):
		self.Tags[Key] = Val
	
	def printout(self):
		print 'Node {0}, {1},{2}'.format(self.NodeID,self.Lat,self.Lon)
		if len(self.Tags)==0:
			print 'No tags'
		else:
			for t in self.Tags.keys():
				print '{0}={1}'.format(t,self.Tags[t])

class OSMWay:
	"""Encapsulate an OSM way"""
	def __init__(self,id=0):
		self.WayID = id
		self.Tags = {}
		self.Nds = []

	def AddTag(self,Key,Val):
		self.Tags[Key] = Val

	def AddNd(self,NdID):
		self.Nds.append(NdID)
	
	def printout(self):
		print 'Way {0}'.format(self.WayID)
		for r in self.Nds:
			print 'ref={0}'.format(r)
		
		if len(self.Tags)==0:
			print 'No tags'
		else:
			for t in self.Tags.keys():
				print '{0}={1}'.format(t,self.Tags[t])

class OSMMember:
	"""Encapsulate an OSM member, part of a relation"""
	def __init__(self,reltype,ref,role):
		self.reltype = reltype
		self.ref = ref
		self.role = role

class OSMRelation:
	def __init__(self,id=0):
		self.RelID = id
		self.Tags = {}
		self.Members = []

	def AddTag(self,Key,Val):
		self.Tags[Key] = Val
      
	def AddMember(self,Member):
		self.Members.append(Member)
	
	def printout(self):
		print 'Relation {0}'.format(self.RelID)
		for m in self.Members:
			print 'type={0}, ref={1}, role={2}'.format(m.reltype,m.ref,m.role)
		
		if len(self.Tags)==0:
			print 'No tags'
		else:
			for t in self.Tags.keys():
				print '{0}={1}'.format(t,self.Tags[t])
      
class OSMHandler(ContentHandler):
	def __init__(self):
		self.Nodes={}
		self.Ways={}
		self.Relations=[]
		self.inNode = False
		self.inWay = False
		self.inRel = False
	
	def startElement(self, name, attrs):
		if name == 'osm': #the base container which is ignored
			pass
		elif name == 'bound': # the limits of the file defined with box.  This is ignored
			pass
		elif name == 'bounds': # the limits of the file defined with min and max. This is ignored
			pass    
		elif name == 'node':
			self.inNode = True
			self.node = OSMNode(int(attrs.get('id')))
			self.node.Lon = float(attrs.get('lon'))
			self.node.Lat = float(attrs.get('lat'))
		elif name == 'way':
			self.inWay = True
			self.way = OSMWay(int(attrs.get('id')))
		elif name == 'relation':
			self.inRel = True
			self.relation = OSMRelation(int(attrs.get('id')))
		elif name == 'tag': # tag values can be utf-8 
			if attrs.get('k') == 'created_by': # ignore created_by
				pass
			elif self.inNode:
				self.node.AddTag(attrs.get('k'),attrs.get('v').encode('utf-8'))
			elif self.inWay:
				self.way.AddTag(attrs.get('k'),attrs.get('v').encode('utf-8'))
			elif self.inRel:
				self.relation.AddTag(attrs.get('k'),attrs.get('v').encode('utf-8'))
		elif name == 'nd':
			if self.inWay:
				self.way.AddNd(attrs.get('ref'))
		elif name == 'member':
			if self.inRel:
				self.member=OSMMember(attrs.get('type'),attrs.get('ref'),attrs.get('role'))
				self.relation.AddMember(self.member)
		else:
			print 'Unknown element {0}'.format(name)

	def endElement(self,name):
		if name == 'node':
			self.Nodes[int(self.node.NodeID)]=self.node
			self.inNode = False
		if name == 'way':
			self.Ways[int(self.way.WayID)]=self.way
			self.inWay = False
		if name == 'relation':
			self.Relations.append(self.relation)
