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

	write_icon_style(fw,"buslocatPlacemark","<href>http://maps.google.com/mapfiles/kml/paddle/wht-stars.png</href>")
	write_icon_style(fw,"startPlacemark","<href>http://maps.google.com/mapfiles/kml/paddle/go.png</href>")
	write_icon_style(fw,"rtatPlacemark","<href>http://maps.google.com/mapfiles/kml/paddle/orange-diamond.png</href>")
	write_icon_style(fw,"adPlacemark","<href>http://maps.google.com/mapfiles/kml/paddle/ylw-square.png</href>")
	write_icon_style(fw,"passPlacemark","<href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>")
	write_icon_style(fw,"normalPlacemark","<href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href>")
	write_icon_style(fw,"highlightPlacemark","<href>http://maps.google.com/mapfiles/kml/paddle/red-stars.png</href>")

	fw.close()

def write_icon_style(fw,style_id,style_data):

	fw.write("<Style id=\"%s\">\n" % style_id)
	fw.write("	<IconStyle>\n")
	fw.write("	<Icon>\n")
	fw.write("		%s\n" % style_data)
	fw.write("	</Icon>\n")
	fw.write("	</IconStyle>\n")
	fw.write("</Style>\n")


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

def write_mark_to_kml_file(kml_file,point_id,coord_list,timestamp,altitude):

	# Google-earthin kml-tiedosto
	#print("write_file: %s" % kml_file)

	#ge_date = "20" + date_year + "-" + date_month + "-" + date_day
	#ge_datetime = ge_date + "T" + timestamp + "Z"

	fw = open(kml_file, 'a')

	fw.write("	<Placemark>\n")
	fw.write("		<TimeStamp>\n")
	#fw.write("			<when>%s</when>\n" % ge_datetime)
	fw.write("			<when>%s</when>\n" % timestamp)
	fw.write("		</TimeStamp>\n")
	#fw.write("		<name>L %s</name>\n" % (counter))
	fw.write("		<description>Locat %s %s</description>\n" % (point_id,timestamp))
	fw.write("		<styleUrl>#buslocatPlacemark</styleUrl>\n")
	fw.write("		<Point>\n")
	fw.write("			<coordinates> \n")

	# Kaydaan linjan paikkapisteet lapi
	for coords in coord_list:
		coord_lon = coords[0]
		coord_lat = coords[1]
		ge_str = "\t\t\t%s,%s,%d\n" % (coord_lon,coord_lat,altitude)
		fw.write(ge_str)
	
	fw.write("			</coordinates>\n")
	fw.write("		</Point>\n")
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