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

import pandas as pd
import os
import json



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

def process_raster_file_from_geoserver(coverage_id, dates,pixelCentroids, output_dir):
    base_url = 'http://197.255.126.45:8080/geoserver/marcnowa/wcs?service=WCS&version=2.0.1&request=GetCoverage'
    bbox = '-35.0,-10.0,38.0,40.0'
    width = 768
    height = 526
    srs = 'EPSG:4326'
    format_type = 'image/geotiff'

    # Wrap dates with tqdm for progress tracking
    for date_str in tqdm(dates, desc="Processing rasters"):
        print(f"\nProcessing raster for date: {date_str}")
        
        # Construct the URL for the current date
        geotiff_url = f"{base_url}&coverageId=marcnowa%3A{coverage_id}_{date_str}&bbox={bbox}&width={width}&height={height}&srs={srs}&styles=&format={format_type}"

        
        # Fetch the GeoTIFF data from the URL
        response = requests.get(geotiff_url)


        # Check if the request was successful
        if response.status_code == 200:
            print(f"Successfully retrieved GeoTIFF for date {date_str}")
            
            # Open the response content as a file-like object using BytesIO
            with rasterio.open(BytesIO(response.content)) as src:
                variable_name = coverage_id

                # Get the original nodata value
                original_nodata = src.nodata

                # # Define the new nodata value
                # nodata = -9999

                # # Read the first band of the raster
                # val = src.read(1)
                # print("Raster data read successfully")

                # # Handle different types of nodata values
                # if original_nodata is None:
                #     print("Original nodata value is None. Setting all NaNs to nodata.")
                #     # Handle NaN values as nodata
                #     val[np.isnan(val)] = nodata
                    
                # elif isinstance(original_nodata, float):
                #     print("Original nodata value is float.")
                #     # Replace the original nodata values with the new nodata value
                #     val[np.isnan(val)] = nodata
                    
                # else:
                #     print("Original nodata value is numeric.")
                #     # Assume nodata is a numerical type that can be compared directly
                #     val[val == original_nodata] = nodata

                # geometry = [Point(src.xy(x, y)[0], src.xy(x, y)[1]) for x, y in np.ndindex(val.shape) if val[x, y] != nodata]
                # print(f"Created {len(geometry)} points from raster data")

                # pointsdf = gpd.GeoDataFrame({'geometry': geometry})
                # pointsdf = pointsdf.set_crs(epsg=4326, inplace=True)

                # pointsdfd = pd.DataFrame({'geometry': pointsdf['geometry']})
                # pointsdfd['UniqueID'] = pointsdfd['geometry'].apply(create_unique_id)
                
                # pointsdfd = gpd.GeoDataFrame(pointsdfd, geometry=pointsdfd['geometry'], crs="EPSG:4326")

                #Add
                pointsdfd = pixelCentroids
                
                
                print("Extracting raster values at points")
                
                raster_values_gdf1 = raster_values_at_points(BytesIO(response.content), pointsdfd, variable_name)

                # Add, Drop points with nan
                raster_values_gdf1 = raster_values_gdf1.dropna(subset=variable_name)

                

                # firstJoin = gpd.sjoin(raster_values_gdf1, bigSQ_all, predicate='intersects')
                # print(f"Performed first spatial join, resulting in {len(firstJoin)} records")

                # firstJoin = firstJoin[['geometry', 'UniqueID', variable_name, 'majorid']]

                # secondJoin = gpd.sjoin(firstJoin, smallSQ_all, predicate='intersects')
                # print(f"Performed second spatial join, resulting in {len(secondJoin)} records")

                # secondJoin = secondJoin[['geometry', 'UniqueID', variable_name, 'majorid', 'minorid']]

                # secondJoin['majorid'] = secondJoin['majorid'].astype(int)
                # secondJoin['minorid'] = secondJoin['minorid'].astype(int)
                # secondJoin['majorid'] = secondJoin['majorid'].astype(str).str.zfill(3)
                # secondJoin['minorid'] = secondJoin['minorid'].astype(str).str.zfill(4)

                #add


                grouped = raster_values_gdf1.groupby('majorid')
                

                for majorid, group in grouped:
                    
                    df = group
                    column_headers = ['date'] + [str(i) for i in df['minorid'].unique()]
                    new_df = pd.DataFrame(columns=column_headers)
                    row = {'date': date_str}
                    for i in df['minorid'].unique():
                        minor_group = df[df['minorid'] == i]
                        if not minor_group.empty:
                            row[str(i)] = minor_group.set_index('UniqueID')[variable_name].to_dict()
                        else:
                            row[str(i)] = {}
                    new_row_df = pd.DataFrame([row])
                    for col in new_row_df.columns[1:]:
                        new_row_df[col] = new_row_df[col].apply(convert_to_double_quotes)
                     
                    csv_prefixName = variable_name.lower()
                    filename = f'{output_dir}/{csv_prefixName}_{majorid}.csv'
                    new_date = new_row_df['date'].iloc[0]

                    if os.path.exists(filename):
                        existing_df = pd.read_csv(filename)
                        existing_df['date'] = existing_df['date'].astype(str)
                        new_row_df['date'] = new_row_df['date'].astype(str)

                        if new_date in existing_df['date'].values:
                            # Entry already exists
                            updated_df = existing_df
                            print(f"Date {new_date} already exists in {filename}. No new entry added.")
                        else:
                            updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
                            # print(f"Appended new entry for date {new_date} to file {filename}.")
                    else:
                        updated_df = new_row_df
                        # print(f"Created new file {filename} with data for date {new_date}.")
                    
                    for col in updated_df.columns[1:]:
                        updated_df[col] = updated_df[col].apply(convert_to_double_quotes)
                    updated_df.to_csv(filename, index=False)
                    # print(f"Saved file {filename}")
        else:
            print(f"Error: Unable to retrieve the GeoTIFF for date {date_str}. Status code: {response.status_code}")


def create_table(file_path, supabase):
    # Load DataFrame from CSV File
    df = pd.read_csv(file_path)
    column_names = df.columns.tolist()

    # Extract Date Column and JSONB Columns
    date_column_name = None
    jsonb_columns = []

    for col in column_names:
        if col.lower() == 'date':
            date_column_name = col
        else:
            jsonb_columns.append(col)

    # Extract Table Name from File Path
    file_name = os.path.basename(file_path).split('.')[0]
    extracted_part = file_name.split('-')[-1]
    table_name = extracted_part.lower()

    # Print Results
    # print(f"Processing File: {file_path}")
    # print("Date Column:", date_column_name)
    # print("JSONB Columns:", jsonb_columns)
    # print("Extracted Part (Table Name):", table_name)

    # Call Supabase SQL Function to Create the Table
    try:
        response = supabase.rpc(
            "create_table_with_dynamic_columns",
            {
                "table_name": table_name,
                "date_column_name": date_column_name,
                "jsonb_columns": jsonb_columns
            }
        ).execute()
        # print(response)  # Show the result of the RPC call
    except Exception as e:
        print(f"An error occurred: {e}")


def upsert_data(file_path, supabase):
    try:
        # Read the DataFrame
        df = pd.read_csv(file_path)
        
        # Extract Table Name from File Path
        file_name = os.path.basename(file_path).split('.')[0]
        extracted_part = file_name.split('-')[-1]
        table_name = extracted_part.lower()
        
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
        print(f"An error occurred while processing file {file_path}: {e}")
