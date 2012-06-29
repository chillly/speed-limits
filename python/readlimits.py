#!/usr/bin/env python

# process an OSM file to extract roads 

import sys
import os.path
import argparse
import codecs
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import MySQLdb as mdb

from osm import *
from hupd import *

__version__='0.1'
__progdesc__='Extract road details from OSM data'

def main():
	#sort out the command line stuff
	parser = argparse.ArgumentParser(description=__progdesc__)
	arga=get_args(parser)
	results = parser.parse_args()
	if arga.inosm=='':
		print '{0} version {1}'.format(__progdesc__,__version__) 
		print 'OSM file name is required (-i)'
		sys.exit(4)
	if not os.path.exists(arga.inosm):
		print '{0} version {1}'.format(__progdesc__,__version__) 
		print 'OSM file {0} cannot be found'.format(arga.inosm)
		sys.exit(5)
	if arga.verbose:
		arga.quiet=False
	if not arga.quiet:
		print '{0} version {1}'.format(__progdesc__,__version__) 
	if arga.verbose:
		print 'Input OSM file: {0}'.format(arga.inosm)
		print 'Text ouput file: {0}'.format(arga.outtxt)
		print 'Quiet mode: {0}'.format(arga.quiet)
		print 'Verbose: {0}'.format(arga.verbose)
	
	# parse the osm file
	OSM = OSMHandler()
	saxparser = make_parser()
	saxparser.setContentHandler(OSM)

	datasource = open(arga.inosm,"r")
	saxparser.parse(datasource)
	datasource.close
		
	print 'Nodes {0}'.format(len(OSM.Nodes))
	print 'Ways {0}'.format(len(OSM.Ways))
	print 'Relations {0}'.format(len(OSM.Relations))
	
	# open the database ready for updates
	h,u,p,d = hupd()
	conn = mdb.connect(h,u,p,d)
	croad = conn.cursor()
	
	hwtype=('motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','tertiary','residential','unclassified')
	
	# find the ways that are highways
	for wid in OSM.Ways.keys():
		way = OSM.Ways[wid]
		if 'highway' in way.Tags and way.Tags['highway'] in hwtype:
			# get north, south east & west max
			n=int(way.Nds[0])
			north = OSM.Nodes[n].Lat
			south = OSM.Nodes[n].Lat
			east = OSM.Nodes[n].Lon
			west = OSM.Nodes[n].Lon	
			for n in way.Nds:
				if north < OSM.Nodes[int(n)].Lat:
					north = OSM.Nodes[int(n)].Lat
				if south > OSM.Nodes[int(n)].Lat:
					south = OSM.Nodes[int(n)].Lat
				if east < OSM.Nodes[int(n)].Lon:
					east = OSM.Nodes[int(n)].Lon
				if west > OSM.Nodes[int(n)].Lon:
					west = OSM.Nodes[int(n)].Lon
			if 'maxspeed' in way.Tags:
				ms = way.Tags['maxspeed']
			else:
				ms=''
			hw=way.Tags['highway']
			#print 'osmid:{0} north:{1} south:{2} east:{3} west:{4} highway:{5} maxspeed:{6}'.format(way.WayID,north,south,east,west,hw,ms)
			croad.execute("INSERT INTO road (osmid,north,south,east,west,highway,maxspeed) VALUES(%s,%s,%s,%s,%s,%s,%s)",(way.WayID,north,south,east,west,hw,ms))
			roadid=croad.lastrowid
			for n in way.Nds:
				lon=OSM.Nodes[int(n)].Lon
				lat=OSM.Nodes[int(n)].Lat
				#print '  roadid: xxx lon:{0} lat:{1}'.format(lon,lat)
				croad.execute("INSERT INTO roadpoints (roadid,lon,lat) VALUES(%s,%s,%s)",(roadid,lon,lat))
	
	conn.close()
	

def get_args(parser):
	'''parse the command line'''
	parser.add_argument('-i', action='store', default='', dest='inosm', help='Input OSM file')
	parser.add_argument('-o', action='store', default='out.txt', dest='outtxt', help='Output text file')
	parser.add_argument('-q', action='store_true', default=False, dest='quiet', help='Process quietly')
	parser.add_argument('-v', action='store_true', default=False, dest='verbose', help='Verbose, overrides quiet (-q)')
	
	results = parser.parse_args()
	return results

if __name__ == '__main__':
	
	main()
