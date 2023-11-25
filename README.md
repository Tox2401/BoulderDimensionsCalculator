# Boulder Dimensions Calculator

This program processes geospatial data from vector (.shp) and raster (.tif) files to generate a dataset containing information about boulders on seabed. It calculates the dimensions, coordinates, and depth of each boulder and exports the results to a new shapefile (.shp).

## Instructions for usage

Boulder Dimensions Calculator has several module dependencies which are not included in Pythons standard library and thus it is recommended to run it using a virtual environment.

Requirements:

- [Python 3.x](https://www.python.org/downloads/)
- [Pandas](https://pypi.org/project/pandas/)
- [Geopandas](https://pypi.org/project/geopandas/)
- [Rasterio](https://pypi.org/project/rasterio/)
- [Shapely](https://pypi.org/project/shapely/)
- [Fiona](https://pypi.org/project/fiona/)

Testing files are included in Github repo:

- Test\_Encoded\_Depths\_File.tif
- Test\_Encoded\_Depths\_File.tif.aux.xml
- Test\_Manually\_Picked\_Boulders.shp
- Test\_Manually\_Picked\_Boulders.dbf
- Test\_Manually\_Picked\_Boulders.prj
- Test\_Manually\_Picked\_Boulders.qix
- Test\_Manually\_Picked\_Boulders.shx

This is console-based program which will prompt user to provide the following data:

- SHP file name
- TIF file name
- Define Block value

![User input prompt](/assets/Image1.png)

**NOTE** : It is necessary for the files to be in the working directory.

The program will generate output files with processed data in the working directory.

![Sample output](/assets/Image2.png)

Output files:

- Output.shp
- Output.dbf
- Output.cpg
- Output.shx

## Functionality

The program utilizes geospatial libraries (geopandas, rasterio, shapely) for handling vector and raster data.

1. The program exports geometry values from .shp file using geopandas and stores them in a list. The type stored is of type Polygon from shapely library.
2. The program iterates through the list of polygon objects and executes several functions to obtain the required data:
  1. Obtains Polygons centroid (defined property of Shapely objects)
  2. Obtains the seabed depth (Checks for the deepest point along the Polygons perimeter)
  3. Obtains the highest point of the boulder (The program creates a mask by cropping .tif data to the limits of the Polygon shape and checks value at each pixel within the mask returning the highest value)
  4. Obtains the depth at polygons centroid point
  5. Obtains centroids coordinates
  6. Calculates the height of the boulder utilizing seabed depth and highest point of the boulder
  7. Calculates boulders length and width (The program generates a rectangle around outer polygon limits, rectangles sides correlate to boulders length and width)
3. Finally, the gathered data for each boulder is saved to pandas DataFrame. Columns "Northing" and "Easting" within dataframe are used to define geometry values for the final .shp file generation.
