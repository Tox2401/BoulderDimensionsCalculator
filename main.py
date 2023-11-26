import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely import Polygon, Point
from fiona.errors import DriverError


def get_boulder_dimensions(polygon):
    """
    Creates rectangle around polygon and returns its length and width as a Tuple representing the largets distance
    within the polygon and the distance within the polygon perpendicular to the length.
    """
    poly = Polygon(polygon)
    rectangle = poly.minimum_rotated_rectangle
    x, y = rectangle.exterior.coords.xy
    edge_length = (Point(x[0], y[0]).distance(Point(x[1], y[1])), Point(x[1], y[1]).distance(Point(x[2], y[2])))
    length = max(edge_length)
    width = min(edge_length)
    return length, width


def get_coordinates(point):
    """
    Returns dictionary with Northing and Easting keys and coordinate values for specified Point object
    :param point:
    :return:
    """
    coordinates = {
        "Northing": point.y,
        "Easting": point.x
    }
    return coordinates


def clean_block_input(string):
    """
    Formats users block input.
    :param string:
    :return:
    """
    return ''.join([c for c in string if c.isalpha() is False])


def get_depth_data(point, depth_data_file):
    """
    Returns depth value of point from specified file. Point parameter can be passed as Tuple or Point object.
    :param point:
    :param depth_data_file:
    :return:
    """
    if isinstance(point, Point):
        lat = point.y
        long = point.x
        row, col = depth_data_file.index(long, lat)
        depth_data = depth_data_file.read(1)

    else:
        lat = point[1]
        long = point[0]
        row, col = depth_data_file.index(long, lat)
        depth_data = depth_data_file.read(1)

    return depth_data[row, col]


def get_deepest_point_around_shape(shape, depth_data_file):
    """
    Iterate through all polygon points and check their depth value, return deepest value as a Tuple.
    :param shape:
    :param depth_data_file:
    :return:
    """
    data = depth_data_file
    deepest_point = get_depth_data(shape.exterior.coords[0], data)
    for point in shape.exterior.coords[:-1]:
        if get_depth_data(point, data) < deepest_point:
            deepest_point = get_depth_data(point, data)
    return deepest_point


def get_highest_point_within_shape(shape, depth_data_file):
    """
    Masks geotiff data to the shape bounds and returns the highest point within the shape.
    :param shape:
    :param depth_data_file:
    :return:
    """
    poly, _ = mask(depth_data_file, [shape], crop=True)
    return poly.max()


def get_relative_depth(seabed_depth, boulder_depth):
    """
    Returns height of a point relative to surrounding seabed.
    :param seabed_depth:
    :param boulder_depth:
    :return:
    """
    return boulder_depth - seabed_depth


def main(vector_file, geotiff_file, block_value):

    index = 0
    shapefile = gpd.read_file(vector_file)
    cleaned_block_input = clean_block_input(block_value)

    # Create a list of "geometry" values from .shp file each of class Polygon from shapely
    boulders = [boulder for boulder in shapefile["geometry"]]

    poly_id = []
    target_id = []
    block = []
    easting = []
    northing = []
    water_depth = []
    length = []
    width = []
    height = []

    with rasterio.open(geotiff_file) as depths_file:
        for boulder in boulders:
            centroid = boulder.centroid
            centroid_coordinates = get_coordinates(centroid)
            seabed_depth = get_deepest_point_around_shape(boulder, depths_file)  # Lowest point along polygon edges
            boulder_depth = get_highest_point_within_shape(boulder, depths_file)  # Highest point within polygon limits

            poly_id.append(index)
            target_id.append(f"MBES_{cleaned_block_input}_{index:02d}")
            block.append(block_input)
            easting.append(centroid_coordinates['Easting'])
            northing.append(centroid_coordinates['Northing'])
            water_depth.append(get_depth_data(centroid, depths_file))  # Depth at the polygon/boulder centroid
            length.append(get_boulder_dimensions(boulder)[0])
            width.append(get_boulder_dimensions(boulder)[1])
            height.append(get_relative_depth(seabed_depth, boulder_depth))  # Height of the boulder
            index += 1

    # Create dataframe with all the processed information
    df = pd.DataFrame(
        {
            "Poly_ID": poly_id,
            "Target_ID": target_id,
            "Block": block,
            "Easting": easting,
            "Northing": northing,
            "WaterDepth": water_depth,
            "Length": length,
            "Width": width,
            "Height": height,
        }
    )

    # Create geometry using Easting and Northing columns in the dataframe
    geometry = [Point(xy) for xy in zip(df['Easting'], df['Northing'])]
    # Export data to .shp file
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    gdf.to_file(filename="Output.shp", index=None)
    print("Complete! Output.shp has been created")


if __name__ == "__main__":

    while True:
        vector_file = input("Enter .shp (vector) file name: ")
        geotiff_file = input("Enter .tif (geotiff) file name: ")
        block_input = input('Enter "Block" value: ')
        print("Processing data.....")
        try:
            main(vector_file, geotiff_file, block_input)
            break
        except DriverError:
            print("---->ERROR<----\n"
                  "Make sure that:\n"
                  "1. Files are located in your current working directory\n"
                  "2. Include file type extension (.shp, .tif)\n")
