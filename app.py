
from flask import Flask, request, jsonify
from src.scripts.computestats import generate_date_range, process_raster_file_from_geoserver, fetch_data_by_date_range
from supabase import create_client, Client
import geopandas as gpd

app = Flask(__name__)


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
    print(f'Inputs: {ocean_variable} for {start_date} to {end_date}')
    
    try:
        # Example parameters for the raster processing
        dates = generate_date_range(start_date, end_date)
        print(f'Dates to process: {dates}')

        pixelCentroids = gpd.read_file('src/data/pixelCentroids/SALT_centroids.shp')
        coverage_id = ocean_variable

        # Call the processing function from computestats.py
        process_raster_file_from_geoserver(coverage_id, dates, pixelCentroids)

        return jsonify({"status": "success", "message": "Raster processing and upload completed."})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    


@app.route('/fetch-data-by-date-range', methods=['POST'])
def fetch_data_route():
    input_json = request.get_json(force=True)
    return fetch_data_by_date_range(input_json)


if __name__ == '__main__':
    app.run(debug=True)