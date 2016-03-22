# -*- coding: cp1252 -*-
"""
###############################################################################
HEADER: 	MapGEkml.py    

AUTHOR:     Esa Heikkinen
DATE:       22.03.2016
DOCUMENT:   - 
VERSION:    "$Id$"
REFERENCES: -
PURPOSE:    
CHANGES:    "$Log$"
###############################################################################
"""


def init_kml_file(kml_file,dataname,datadescription):

	# Google-earthin kml-tiedosto
	print("write_file: %s" % kml_file)
	fw = open(kml_file, 'w')

	# Google-earth kml-tiedoston alkutekstit
	fw.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
	fw.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
	fw.write("  <Document>\n")
	fw.write("	<name>%s</name>\n" % dataname)
	fw.write("	<description>%s\n" % datadescription)
	fw.write("	</description>\n")
	
	fw.write("	<Style id=\"yellowLineGreenPoly\">\n")
	fw.write("	  <LineStyle>\n")
	fw.write("		<color>7f00ffff</color>\n")
	fw.write("		<width>4</width>\n")
	fw.write("	  </LineStyle>\n")
	fw.write("	  <PolyStyle>\n")
	fw.write("		<color>7f00ff00</color>\n")
	fw.write("	  </PolyStyle>\n")
	fw.write("	</Style>\n")
	
	fw.write("	<Style id=\"myStyle\">\n")
	fw.write("	  <LineStyle>\n")
	fw.write("		<color>ffff00ff</color>\n")
	#fw.write("		<colorMode>random</colorMode>\n")
	fw.write("		<width>4</width>\n")
	fw.write("	  </LineStyle>\n")
	fw.write("	  <PolyStyle>\n")
	fw.write("		<color>7f00ff00</color>\n")
	fw.write("	  </PolyStyle>\n")
	fw.write("	</Style>\n")
	
	fw.write("	<Style id=\"myStyle2\">\n")
	fw.write("	  <LineStyle>\n")
	fw.write("		<color>ff00ffff</color>\n")
	#fw.write("		<colorMode>random</colorMode>\n")
	fw.write("		<width>4</width>\n")
	fw.write("	  </LineStyle>\n")
	fw.write("	  <PolyStyle>\n")
	fw.write("		<color>7f00ff00</color>\n")
	fw.write("	  </PolyStyle>\n")
	fw.write("	</Style>\n")
	
	fw.write("	<Style id=\"myStyle3\">\n")
	fw.write("	  <LineStyle>\n")
	fw.write("		<color>ff0000ff</color>\n")
	#fw.write("		<colorMode>random</colorMode>\n")
	fw.write("		<width>4</width>\n")
	fw.write("	  </LineStyle>\n")
	fw.write("	  <PolyStyle>\n")
	fw.write("		<color>7f00ff00</color>\n")
	fw.write("	  </PolyStyle>\n")
	fw.write("	</Style>\n")
	
	fw.write("	<Style id=\"myStyle4\">\n")
	fw.write("	  <LineStyle>\n")
	fw.write("		<color>ff00ff00</color>\n")
	#fw.write("		<colorMode>random</colorMode>\n")
	fw.write("		<width>4</width>\n")
	fw.write("	  </LineStyle>\n")
	fw.write("	  <PolyStyle>\n")
	fw.write("		<color>7f00ff00</color>\n")
	fw.write("	  </PolyStyle>\n")
	fw.write("	</Style>\n")

	fw.close()

def write_area_to_kml_file(kml_file,area_id,coord_list,altitude):

	# Google-earthin kml-tiedosto
	#print("write_file: %s" % kml_file)
	fw = open(kml_file, 'a')

	# Google-earth kml-tiedoston path:in alkutekstit
	fw.write("	<Placemark>\n")
	fw.write("	  <name>Area</name>\n")
	fw.write("	  <description>%s</description>\n" % area_id)
	fw.write("	  <styleUrl>#myStyle2</styleUrl>\n")
	fw.write("	  <LineString>\n")
	fw.write("		<extrude>1</extrude>\n")
	fw.write("		<tessellate>1</tessellate>\n")
	fw.write("		<altitudeMode>absolute</altitudeMode>\n")
	fw.write("		<coordinates> \n")
	
	# Kaydaan linjan paikkapisteet lapi
	for coords in coord_list:
		
		coord_lon = coords[0]
		coord_lat = coords[1]
		ge_str = "\t\t\t%s,%s,%d\n" % (coord_lon,coord_lat,altitude)
		fw.write(ge_str)
		
	# Google-earth kml-tiedoston path:in lopputekstit
	fw.write("		</coordinates>\n")
	fw.write("	  </LineString>\n")
	fw.write("	</Placemark>\n")

	fw.close()

def write_line_to_kml_file(kml_file,line_id,coord_list,altitude):

	# Google-earthin kml-tiedosto
	#print("write_file: %s" % kml_file)
	fw = open(kml_file, 'a')

	# Google-earth kml-tiedoston path:in alkutekstit
	fw.write("	<Placemark>\n")
	fw.write("	  <name>Line</name>\n")
	fw.write("	  <description>%s</description>\n" % line_id)
	fw.write("	  <styleUrl>#myStyle</styleUrl>\n")
	fw.write("	  <LineString>\n")
	fw.write("		<extrude>1</extrude>\n")
	fw.write("		<tessellate>1</tessellate>\n")
	#fw.write("		<altitudeMode>absolute</altitudeMode>\n")
	fw.write("		<altitudeMode>clampToGround</altitudeMode>\n")
	fw.write("		<coordinates> \n")
	
	# Kaydaan linjan paikkapisteet lapi
	for coords in coord_list:
		
		coord_lon = coords[0]
		coord_lat = coords[1]
		ge_str = "\t\t\t%s,%s,%d\n" % (coord_lon,coord_lat,altitude)
		fw.write(ge_str)
		
	# Google-earth kml-tiedoston path:in lopputekstit
	fw.write("		</coordinates>\n")
	fw.write("	  </LineString>\n")
	fw.write("	</Placemark>\n")

	fw.close()

def write_point_to_kml_file(kml_file,point_id,coord_list,altitude):

	# Google-earthin kml-tiedosto
	#print("write_file: %s" % kml_file)
	fw = open(kml_file, 'a')

	# Google-earth kml-tiedoston path:in alkutekstit
	fw.write("	<Placemark>\n")
	fw.write("	  <name>%s</name>\n" % point_id)
	fw.write("	  <description>%s</description>\n" % point_id)
	fw.write("		<Point>\n")
	fw.write("		<coordinates>\n")
	
	# Kaydaan linjan paikkapisteet lapi
	for coords in coord_list:
		
		coord_lon = coords[0]
		coord_lat = coords[1]
		ge_str = "\t\t\t%s,%s,%d\n" % (coord_lon,coord_lat,altitude)
		fw.write(ge_str)
		
	# Google-earth kml-tiedoston path:in lopputekstit
	fw.write("		</coordinates>\n")
	fw.write("	  </Point>\n")
	fw.write("	</Placemark>\n")

	fw.close()

def finalize_kml_file(kml_file):

	# Google-earthin kml-tiedosto
	print("write_file: %s" % kml_file)
	fw = open(kml_file, 'a')

	# Google-earth kml-tiedoston lopputekstit
	fw.write("  </Document>\n")
	fw.write("</kml>\n")

	fw.close()