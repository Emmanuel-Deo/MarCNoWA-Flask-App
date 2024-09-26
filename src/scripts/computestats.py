from tqdm import tqdm
import requests
import rasterio
from io import BytesIO
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
import os
from datetime import datetime, timedelta
from supabase import create_client, Client
import pandas as pd
import os
import json


url = "https://admin.geoportal.gmes.ug.edu.gh"
key =  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"
supabase = create_client(url, key)

def fetch_data_by_date_range(input_json):
    # Extract parameters from the input JSON
    start_date = input_json.get('startdate', None)
    end_date = input_json.get('enddate', None)
    table_name = input_json.get('tablename', None)
    jsonb_column_name = input_json.get('jsonbcolumnname', None)
    pixel_id = input_json.get('pixelid', None)

    # Log input values for debugging
    print(f"Start Date: {start_date}, End Date: {end_date}, Table Name: {table_name}, JSONB Column Name: {jsonb_column_name}, Pixel ID: {pixel_id}")

    # Check for None values
    if None in (start_date, end_date, table_name, jsonb_column_name, pixel_id):
        return {"error": "All fields are required."}, 400

    # Call the fetch_rows_by_pixel_id function
    response = supabase.rpc("fetch_rows_by_pixel_id_i", {
        "start_date": start_date,
        "end_date": end_date,
        "table_name": table_name,
        "jsonb_column_name": jsonb_column_name,
        "pixel_id": pixel_id
    }).execute()

    data = response.data
    return data


# Define a function to create unique IDs
def create_unique_id(geometry):
    lat, lon = geometry.xy
    lat_str = f"P{str(abs(lat[0])).replace('.', 'D')}" if lat[0] >= 0 else f"N{str(abs(lat[0])).replace('.', 'D')}"
    lon_str = f"P{str(abs(lon[0])).replace('.', 'D')}" if lon[0] >= 0 else f"N{str(abs(lon[0])).replace('.', 'D')}"
    lat_str = lat_str[:12]
    lon_str = lon_str[:12]
    unique_id = f"{lat_str}C{lon_str}"
    return unique_id

# Define a function to get raster values at points
def raster_values_at_points(raster_path, points_gdf, column_name):
    new_gdf = points_gdf.copy()
    coords = [(point.x, point.y) for point in points_gdf.geometry]
    with rasterio.open(raster_path) as src:
        new_gdf[column_name] = [x[0] for x in src.sample(coords)]
    return new_gdf

# Define a function to read vector data
def read_vector_data(bigSQ_path, smallSQ_path, pixelCentroids_path):
    bigSQ_all = gpd.read_file(bigSQ_path)
    bigSQ_all = bigSQ_all.rename(columns={"id": "majorid"})
    
    smallSQ_all = gpd.read_file(smallSQ_path)
    smallSQ_all = smallSQ_all.rename(columns={"id": "minorid"})
    
    pixelCentroids_all = gpd.read_file(pixelCentroids_path)
    return bigSQ_all, smallSQ_all, pixelCentroids_all
    
def convert_to_double_quotes(d):
    return str(d).replace("'", '"')



def generate_date_range(start_date, end_date):
    # Convert strings to datetime objects
    start = datetime.strptime(start_date, "%Y%m%d")
    end = datetime.strptime(end_date, "%Y%m%d")
    
    # Generate the list of dates
    date_list = []
    current_date = start
    while current_date <= end:
        date_list.append(current_date.strftime("%Y%m%d"))
        current_date += timedelta(days=1)
    
    return date_list

def upsert_data(df,name):
    try:
        table_name =name
        
        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            # Extract the date
            date_value = row['date']
            
            # Create the dictionary with the date
            upsert_data = {
                'date': date_value,
            }
            
            # Iterate over JSONB columns
            for col in df.columns:
                if col != 'date':
                    # Parse JSONB data
                    json_data = json.loads(row[col])
                    
                    # Add JSONB data to the dictionary
                    upsert_data[col] = json_data
            
            # Upsert the data into the Supabase table
            try:
                response = supabase.table(table_name).upsert(
                    upsert_data,
                    on_conflict=['date'],  # Specify the column(s) to check for conflicts
                ).execute()
                # Uncomment the following line to print the response
                # print(f"Upserted row {index} with response: {response}")
            except Exception as e:
                print(f"An error occurred while upserting row {index} in table {table_name}: {e}")

    except Exception as e:
        print(f"An error occurred while processing file {name}: {e}")

def process_raster_file_from_geoserver(coverage_id, dates, pixelCentroids):
    base_url = 'http://197.255.126.45:8080/geoserver/marcnowa/wcs?service=WCS&version=2.0.1&request=GetCoverage'
    bbox = '-35.0,-10.0,38.0,40.0'
    width = 768
    height = 526
    srs = 'EPSG:4326'
    format_type = 'image/geotiff'

    # Wrap dates with tqdm for progress tracking
    for date_str in tqdm(dates, desc="Processing rasters"):
        print(f"\nInitializing Raster Processing for: {coverage_id}_{date_str}")

        # Construct the URL for the current date
        geotiff_url = f"{base_url}&coverageId=marcnowa%3A{coverage_id}_{date_str}&bbox={bbox}&width={width}&height={height}&srs={srs}&styles=&format={format_type}"

        # Fetch the GeoTIFF data from the URL
        response = requests.get(geotiff_url)

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Error: Unable to retrieve the GeoTIFF for date {coverage_id}_{date_str}. Status code: {response.status_code}")

        print(f"Successfully retrieved GeoTIFF for {coverage_id}_{date_str}")

        # Open the response content as a file-like object using BytesIO
        with rasterio.open(BytesIO(response.content)) as src:
            variable_name = coverage_id


            pointsdfd = pixelCentroids

            print(f"Extracting raster values at points for {coverage_id}_{date_str}")

            raster_values_gdf1 = raster_values_at_points(BytesIO(response.content), pointsdfd, variable_name)

            # Drop points with nan
            raster_values_gdf1 = raster_values_gdf1.dropna(subset=variable_name)

            # Drop column 'geometry'
            raster_values_gdf1 = raster_values_gdf1.drop('geometry', axis=1)

            # Round to 4
            raster_values_gdf1[variable_name] = raster_values_gdf1[variable_name].round(4)

            df = raster_values_gdf1

            # Using itertuples() to loop over rows
            df_dict = {}

            for row in df.itertuples(index=False):
                major = (f'{coverage_id}_{row.majorid}').lower()
                minor = row.minorid
                uniqueid = row.UniqueID
                variableValue = getattr(row, coverage_id)

                if major not in df_dict:
                    df_dict[major] = {}

                if minor not in df_dict[major]:
                    df_dict[major][minor] = {}

                df_dict[major][minor][uniqueid] = variableValue

            data_dict = df_dict

            dataframes = {}

            for key, nested_dict in data_dict.items():
                # Prepare the data for the DataFrame
                df_data = {minor_id: [uni_dict] for minor_id, uni_dict in nested_dict.items()}

                # Create the DataFrame
                df = pd.DataFrame(df_data)

                # Add the 'date' column at the beginning
                df.insert(0, 'date', date_str)

                for col in df.columns[1:]:
                    df[col] = df[col].apply(convert_to_double_quotes)

                # Store in the dictionary
                dataframes[key] = df

            print("Successfully generated all dataframes")

            # Apply the upload function to each DataFrame in dataframes
            for name, df in dataframes.items():
                print(f"\nUploading day {date_str} entry for Grid {name}:")
                upsert_data(df, name)