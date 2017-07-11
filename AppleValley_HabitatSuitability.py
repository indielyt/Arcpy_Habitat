# IN progress

# Script for extracting suitable habitat for fish species in Apple Valley Project (N. St. Vrain) outside of Lyons, CO
# Existing and proposed rasters should be in separate folders and run separately.  Distinct event flows should be 
# separate folders and run separately
# Must update condition variable, parameters, workspace and output workspace.

import os
import arcpy
from arcpy import env
from arcpy.sa import *
import numpy

# define parameters for habitat suitability, value is a SQL query used in extractions
rh_d = "Value <= 1"
rh_v = "Value <= 0.82"
dph_d = "Value >= 2"
dph_v = "Value <= 0.82"

# Define existing or proposed (e, p) model run and event (100, 50, 25, 10, bkf, lf). i.e. p100  Do not go over 13 characters total
condition = "pbkf"

# Environment Settings: Workspace setting and a variable called workspace for constructing file names
arcpy.env.workspace = r"C:\DanielProjects\AV_HabitatSuitability\habitat_bkf_data_proposed"
outworkspace = r"C:\DanielProjects\AV_HabitatSuitability\habitat_bkf_proposed_results"
arcpy.env.overwriteOutput = True

#check out Spatial Analyst Extension
arcpy.CheckOutExtension("Spatial") # check out ArcGIS Spatial Analyst

# create list of rasters in workspace
rasters = arcpy.ListRasters("","GRID")

# #Set this raster as the snap raster for other operations
# arcpy.env.snapRaster = temp_raster1

# define file pathways and names as inputs/outputs for geoprocessing
temp_raster1 = os.path.join("in_memory", "1")   # store in_memory, rearing habitat suitable depths.
temp_raster2 = os.path.join("in_memory", "2")   # store in_memory, deep pool habitat suitable depths
temp_raster3 = os.path.join("in_memory", "3")   # store in_memory, rearing habitat suitable velocities
temp_raster4 = os.path.join("in_memory", "4")   # store in_memory, deep pool habitat suitable velocities
temp_raster5 = os.path.join("in_memory", "5")   # store in_memory, con raster rearing habitat suitable depths
temp_raster6 = os.path.join("in_memory", "6")   # store in_memory, con raster deep pool habitat suitable depths
temp_raster7 = os.path.join("in_memory", "7")   # store in_memory, con raster rearing habitat suitable velocities
temp_raster8 = os.path.join("in_memory", "8")   # store in_memory, con raster deep pool habitat suitable velocities
temp_raster9 = os.path.join("in_memory", "9")   # store in_memory, plus raster from depth and velocity (rearing habitat)
temp_raster10 = os.path.join("in_memory", "10") # store in_memory, plus raster from depth and velocity (deep pool habitat)

outraster1 = os.path.join(outworkspace,condition + "_rearing")
outraster2 = os.path.join(outworkspace,condition + "_pool")

# iterate through each raster in the list
for raster in rasters:
	# define names of intermediary rasters and output raster (must be less than 13 characters)
	abbreviation = raster[0] # get first letter
	split = raster.split("_") # split input feature path at underscores
	variable = split[1] # fetch analysis type (d-depth, v-velocity)

	# extract suitable raster values for depth and velocity at rearing habitat (rh) 
	if variable == "d":
		rh_d_raster = ExtractByAttributes(raster, rh_d)  # extract suitable rearing habitat depths
		rh_d_raster.save(temp_raster1)
		dph_d_raster = ExtractByAttributes(raster, dph_d) # extract suitable deep pool habitat depths
		dph_d_raster.save(temp_raster2)
	if variable == "v":
		rh_v_raster = ExtractByAttributes(raster, rh_v)  # extract suitable rearing habitat velocities
		rh_v_raster.save(temp_raster3)
		dph_v_raster = ExtractByAttributes(raster, dph_v) # extract suitable deep pool habitat velocities
		dph_v_raster.save(temp_raster4)



# Create conditional rasters with values of 0 where not suitable, values of 1 for suitable rearing habitat 
# depths and velocities, values of 10 for suitable deep pool habitat depths and velocities.

# Rearing habitat depths
Con_rh_d = Con(temp_raster1, 1, 0, "Value > 0" ) # convert suitable rh depths to values of 1, zero elsewhere
Con_rh_d.save(temp_raster5)
# Deep pool habitat depths
Con_dph_d = Con(temp_raster2, 10, 0, "Value > 0" ) # convert suitable dph depths to values of 10, zero elsewhere
Con_dph_d.save(temp_raster6)
# Rearing habitat velocities
Con_rh_v = Con(temp_raster3, 1, 0, "Value > 0" ) # convert suitable rh velocites to values of 1, zero elsewhere
Con_rh_v.save(temp_raster7)
# Deep pool habitat velocities
Con_dph_v = Con(temp_raster4, 10, 0, "Value > 0" ) # convert suitable dph depths to values of 10, zero elsewhere
Con_dph_v.save(temp_raster8)


# Add the "reclassified" raster ouputs from the Con statements.  Values of 2 will be suitable for 
# rearing habitat, values of 20 will be suitable habitat for deep pool habitat
rh_plus = Plus(temp_raster5,temp_raster7)
rh_plus.save(temp_raster9)
dph_plus = Plus(temp_raster6,temp_raster8)
dph_plus.save(temp_raster10)


# Extract suitable habitat from previous "Plus" rasters.Values of 2 will be suitable for 
# rearing habitat, values of 20 will be suitable habitat for deep pool habitat
rh_habitat =  ExtractByAttributes(temp_raster9,"Value = 2")
rh_habitat.save(outraster1)

dph_habitat =  ExtractByAttributes(temp_raster10,"Value = 20")
dph_habitat.save(outraster2)

# Compute statistics for area of suitable rearing habitat - OUTPUTS INFO TABLE
inZoneData = outraster1
inValueRaster = outraster1
zoneField = "COUNT"
outTable = os.path.join(outworkspace,outraster1 + "_table")
outZSat = ZonalStatisticsAsTable(inZoneData, zoneField,inValueRaster,outTable,"","SUM")

# # Compute statistics for area of suitable rearing habitat and export to numpy and then csv
# inZoneData = outraster1
# inValueRaster = outraster1
# zoneField = "COUNT"
# temp_table1 = os.path.join("in_memory", "table1")
# outZSat = ZonalStatisticsAsTable(inZoneData, zoneField,inValueRaster,temp_table1,"","SUM")
# arr1 = arcpy.da.TableToNumPyArray(temp_table1,"AREA")
# outTable1 = os.path.join(outworkspace,outraster1 + "_table.csv")
# numpy.savetxt(outTable1,arr1,delimiter=",")

# Compute statistics for area of suitable deep pool habitat - OUTPUTS INFO TABLE
inZoneData = outraster2
inValueRaster = outraster2
zoneField = "COUNT"
outTable = os.path.join(outworkspace,outraster2 + "_table")
outZSat = ZonalStatisticsAsTable(inZoneData, zoneField,inValueRaster,outTable,"","SUM")

# # Compute statistics for area of suitable deep pool habitat and export to numpy and then csv
# inZoneData = outraster2
# inValueRaster = outraster2
# zoneField = "COUNT"
# temp_table2 = os.path.join("in_memory", "table2")
# outZSat = ZonalStatisticsAsTable(inZoneData, zoneField,inValueRaster,temp_table2,"","SUM")
# arr2 = arcpy.da.TableToNumPyArray(temp_table2,"AREA")
# outTable2 = os.path.join(outworkspace,outraster2 + "_table.csv")
# numpy.savetxt(outTable2,arr2,delimiter=",")



# Check in spatial analyst
arcpy.CheckInExtension("Spatial")

# Delete in-memory objects
arcpy.Delete_management("in_memory")

