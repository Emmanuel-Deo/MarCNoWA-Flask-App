
from flask import Flask, request, jsonify
from src.scripts.computestats import generate_date_range, read_vector_data, process_raster_file_from_geoserver, create_table, upsert_data
from supabase import create_client, Client
import os
import geopandas as gpd
import json

app = Flask(__name__)

url = "https://admin.geoportal.gmes.ug.edu.gh"
key =  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"
supabase = create_client(url, key)

@app.route('/test', methods=['POST'])
def test():
# Get JSON data from the request
    input_json = request.get_json(force=True)
    
    # Extract startdate from the JSON payload
    startdate = input_json.get('startdate', None)
    
    # Print startdate to the console (for debugging purposes)
    print(f"Start Date: {startdate}")
    
    # Check if startdate matches the specified value
    if startdate == "2024-09-16":
        return jsonify({"message": "Hello World"})
    
    # If startdate does not match, return the startdate in the response
    return jsonify({"startdate": startdate})

@app.route('/run-compute-stats', methods=['POST'])
def run_compute_stats():
    input_json = request.get_json(force=True)
    start_date = input_json.get('startdate', None)
    end_date = input_json.get('enddate', None)
    ocean_variable = input_json.get('variable', None)
    print(start_date)
    try:
        # Example parameters for the raster processing
        dates = generate_date_range(start_date, end_date)
        pixelCentroids = gpd.read_file('src/data/pixelCentroids/SALT_centroids.shp')
        coverage_id = ocean_variable
        output_dir = f'src/outputs/csvs/{coverage_id.lower()}'

        # Call the processing function from computestats.py
        process_raster_file_from_geoserver(coverage_id, dates, pixelCentroids, output_dir)

        folder_path = output_dir
        file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]

        # Create Table
        for file_path in file_paths:
            create_table(file_path, supabase)

        # Upsert data into each table
        for file_path in file_paths:
            upsert_data(file_path, supabase)
        
        return jsonify({"status": "success", "message": "Raster processing and upload completed."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)