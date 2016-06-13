;#######################################################################
;# 
;#	SSDPrep_ELMI_busstops.tcl
;#	
;#	Konvertoi ELMI:n pysäkitiedot (pääte- ja normaalipysäkit) LOGDIG:in ymmärtämään muotoon
;#
;#	11.6.2016 Esa
;#
;#######################################################################
	
set g_RCS_ID	"V1 13.6.2016 SSDPrep_ELMI_busstops.tcl \$Id$"

# Reads the coordinates of all terminal bussstops
source EPT_config_terminal_busstops.tcl

# Reads the data of signs for checking
source EPT_config_signs.tcl

#########################################################################################
proc convert_terminal_busstops { directory filename } {

	global g_busstop_list 
	global g_busstop_array 

	puts "convert_terminal_busstops"

	set coord_cnt 0
	set coord_warning_cnt 0	
	foreach busstop $g_busstop_list {

		if { [info exists g_busstop_array($busstop)] == 1 } {
			#puts "busstop=$g_busstop_array($busstop)"

			array set busstop_data_array $g_busstop_array($busstop)

			if { [info exists busstop_data_array(lat)] == 1 } {
				set first_char [string index $busstop_data_array(lat) 0]
				if { [string compare $first_char U] != 0 } {
				
					incr coord_cnt

					set lat $busstop_data_array(lat)
					set lon $busstop_data_array(lon)
					set SW_lat $busstop_data_array(SW_lat)
					set SW_lon $busstop_data_array(SW_lon)
					set NE_lat $busstop_data_array(NE_lat)
					set NE_lon $busstop_data_array(NE_lon)

					#puts "busstop=$busstop, lat=$lat, lon=$lon"

					# Joskus koordinaatit voi olla väärinpäin alkuperäisessä datassa ??
					set warn_flag 0
					if { $SW_lat > $NE_lat} {
						puts "WARN: Latitude: SW: $SW_lat > NE: $NE_lat"

						# Käännetään koordinaatit
						set NE_lat_old $NE_lat
						set NE_lat $SW_lat
						set SW_lat $NE_lat_old

						set warn_flag 1
					}
					if { $SW_lon > $NE_lon} {
						puts "WARN: Longitude: SW: $SW_lon > NE: $NE_lon"

						# Käännetään koordinaatit
						set NE_lon_old $NE_lon
						set NE_lon $SW_lon
						set SW_lon $NE_lon_old

						set warn_flag 1
					}

					if { $warn_flag == 1} {
						incr coord_warning_cnt
					}
					
					# Lisätään etunollat linjan nimeen
					set cnt [expr { 7 - [string length $busstop]}]
					if { $cnt > 0 } {
						set zeros [string repeat "0" $cnt]	
						set busstop_new [format "%s%s" $zeros $busstop]
					} else {
						set busstop_new $busstop
					}
					set filepathname [format "%s/%s_%s.csv" $directory $filename $busstop_new]

					#write_file $directory $filename $busstop $lat $lon $SW_lat $SW_lon $NE_lat $NE_lon
					write_file $directory $filename $busstop_new $lat $lon $SW_lat $SW_lon $NE_lat $NE_lon
				}
			}
		}
	}

	puts "coord_cnt=$coord_cnt, coord_warning_cnt=$coord_warning_cnt"

}

#########################################################################################
proc convert_target_busstops { directory filename } {

	global g_sign_list 
	global g_sign_array 

	puts "convert_target_busstops"

	foreach busstop $g_sign_list {

		if { [info exists g_sign_array($busstop)] == 1 } {
			#puts "busstop=$g_busstop_array($busstop)"

			array set busstop_data_array $g_sign_array($busstop)

			if { [info exists busstop_data_array(lat_ms)] == 1 } {
				set first_char [string index $busstop_data_array(lat_ms) 0]
				if { [string compare $first_char U] != 0 } {
				
					set order_num $busstop_data_array(order_num)
					set name $busstop_data_array(name)
					set lat_ms $busstop_data_array(lat_ms)
					set lon_ms $busstop_data_array(lon_ms)
					set direc $busstop_data_array(direc)
					set len_ad $busstop_data_array(len_ad)
					set len $busstop_data_array(len)
					set w1 $busstop_data_array(w1)
					set w2 $busstop_data_array(w2)
					set log_control $busstop_data_array(log_control)
										
					#puts "busstop=$busstop, order_num=$order_num, lon=$lon"

					# Converts meter-values to millisecond-format	
					if { $direc == "E" || $direc == "W" } {
						set len_ad_ms 	[expr {round($len_ad / 0.015)}]
						set len_ms		[expr {round($len / 0.015)}]
						set w1_ms		[expr {round($w1 / 0.03)}]
						set w2_ms		[expr {round($w2 / 0.03)}]	
					} else {
						set len_ad_ms 	[expr {round($len_ad / 0.03)}]
						set len_ms		[expr {round($len / 0.03)}]
						set w1_ms		[expr {round($w1 / 0.015)}]
						set w2_ms		[expr {round($w2 / 0.015)}]			
					}
					
					# Calculates limits for the busstop-area
					# From West
					if { $direc == "W" } {
						set lat_sign_high [expr {$lat_ms + $w1_ms}]
						set lat_sign_low  [expr {$lat_ms - $w2_ms}]
						set lon_sign_high [expr {$lon_ms + $len_ms - $len_ad_ms}]
						set lon_sign_low  [expr {$lon_ms - $len_ad_ms}]
						set g_position_sign $lon_sign_low
						
					# From South
					} elseif { $direc == "S"} {
						set lat_sign_high [expr {$lat_ms - $len_ad_ms + $len_ms}]
						set lat_sign_low  [expr {$lat_ms - $len_ad_ms}]
						set lon_sign_high [expr {$lon_ms + $w2_ms}]
						set lon_sign_low  [expr {$lon_ms - $w1_ms} ]
						set g_position_sign $lat_sign_high
						
					# From North
					} elseif { $direc == "N"} {
						set lat_sign_high [expr {$lat_ms + $len_ad_ms}]
						set lat_sign_low  [expr {$lat_ms + $len_ad_ms - $len_ms}]
						set lon_sign_high [expr {$lon_ms + $w2_ms}]
						set lon_sign_low  [expr {$lon_ms - $w1_ms}]
						set g_position_sign $lat_sign_low
								
					# From East and other directions		
					} else {
						set lat_sign_high [expr {$lat_ms + $w1_ms}]
						set lat_sign_low  [expr {$lat_ms - $w2_ms}]
						set lon_sign_high [expr {$lon_ms + $len_ad_ms}]
						set lon_sign_low  [expr {$lon_ms + $len_ad_ms - $len_ms}]
						set g_position_sign $lon_sign_high
					}
					
					set lon_sign_high_aadddd [move_ms_to_AADDDD $lon_sign_high]
					set lon_sign_low_aadddd  [move_ms_to_AADDDD $lon_sign_low]
					set lat_sign_high_aadddd [move_ms_to_AADDDD $lat_sign_high]
					set lat_sign_low_aadddd  [move_ms_to_AADDDD $lat_sign_low]
					set lat_aadddd  [move_ms_to_AADDDD $lat_ms]
					set lon_aadddd  [move_ms_to_AADDDD $lon_ms]

					write_file $directory $filename $busstop $lat_aadddd $lon_aadddd \
						$lat_sign_low_aadddd $lon_sign_low_aadddd \
						$lat_sign_high_aadddd $lon_sign_high_aadddd
				}
			}
		}
	}
}

#########################################################################################
# Converts coordinates from ms-format to AADDDD-format.
proc move_ms_to_AADDDD { coord_ms } {

	# Muutetaan koordinaatit millisekunttimuodosta muotoon aa.dddd
	set coord_aadddd [expr {$coord_ms / 3600000.0}]
	return $coord_aadddd
}

#########################################################################################
proc write_file { directory filename busstop lat lon SW_lat SW_lon NE_lat NE_lon } {

	set filepathname [format "%s/%s_%s.csv" $directory $filename $busstop]
	puts "write_file: $filepathname"

	set fileID [open $filepathname w]

	puts $fileID "Counter\tLongitude\tLatitude"
	set line [format "1\t%s\t%s" $SW_lon $SW_lat]
	puts $fileID $line
	set line [format "2\t%s\t%s" $SW_lon $NE_lat]
	puts $fileID $line
	set line [format "3\t%s\t%s" $NE_lon $NE_lat]
	puts $fileID $line
	set line [format "4\t%s\t%s" $NE_lon $SW_lat]
	puts $fileID $line

	close $fileID

}

#########################################################################################
# Tasta alkaa (paaohjelma) 

puts "Script version    = $g_RCS_ID"

if {$argc > 0} {
	#puts "argc: $argc, argv: $argv"
	set arg_dir	[lindex $argv 0]

} else {
	puts "Usage: tclsh SSDPrep_ELMI_busstops.tcl <output directory>"
	exit
}

puts "arg_dir=$arg_dir"

convert_terminal_busstops $arg_dir "terminal_busstop"
convert_target_busstops $arg_dir "target_busstop"
