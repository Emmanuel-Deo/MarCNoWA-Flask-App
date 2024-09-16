# MarCNoWA Flask App

The MarCNoWA Flask App is designed to efficiently manage and analyze large oceanographic datasets using a grid-based approach. This application leverages Flask for backend operations, with a focus on optimizing performance and scalability in handling raster data.

## Project Description

### Data Gridding

The grid-based organization of raster data into a relational database offers significant benefits for both backend processing and frontend user experience. By facilitating efficient time-series analysis and enhancing application performance, this approach provides a scalable, user-friendly solution for managing and analyzing large oceanographic datasets.

#### Benefits of Grid-Based Data Structuring

1. **Efficiency in Time-Series Analysis**

   - **Pre-Processed Data:** Data is organized into grids, allowing easy access to specific spatial and temporal segments without loading entire rasters.
   - **Direct Queries:** Users can query specific grids for specific dates, reducing computational resources and time required for analysis.
   - **Simplified Computations:** Operations like trend calculations and anomaly detection are streamlined due to the organized data structure.

2. **Enhanced Application Performance**

   - **Selective Data Retrieval:** Only the necessary grid data is fetched, minimizing data load and processing requirements.
   - **Reduced Data Load:** By transmitting only relevant grid data, the application performs faster and provides a smoother user experience.
   - **Scalability:** The grid-based structure allows for efficient scaling as datasets grow, maintaining fast and responsive interactions.

#### Gridding Process

1. **Grid Formation**

   - **Grids Creation:** Raster extents are divided into equal squares. The dimensions match the raster's resolution and extent.
   - **Coordinate Reference System (CRS):** Ensures spatial alignment between grids and rasters.

2. **Creation of Sub-Grids**

   - **Hierarchical Structure:** Smaller grids within larger ones allow detailed spatial analysis. Each smaller grid corresponds to a column in the table.

3. **Pixel Assignment**

   - **Identification of Pixel Centroids:** Pixels are assigned to grids based on their centroid coordinates.
   - **Generation of Unique Identifiers:** Each pixel's latitude and longitude are encoded into a unique identifier for easy spatial queries.
   - **JSONB Format Storage:** Pixel values are stored in JSONB format for complex data structures.

4. **Date Column Addition**

   - Each table includes a date column, crucial for time-series analysis of oceanographic variables.

5. **Final Database Table Structure**

   - **Date Column:** Represents the day of the raster data.
   - **Columns for Smaller Grids:** Each column stores raster pixel values in JSONB format, corresponding to smaller grids.

## Project Setup

### Create an Environment

To get started, create a project folder and a virtual environment.

#### macOS/Linux

1. Open your terminal.
2. Run the following commands:

    ```bash
    mkdir marcnowa-flask-app
    cd marcnowa-flask-app
    python3 -m venv .venv
    ```

#### Windows

1. Open Command Prompt or PowerShell.
2. Run the following commands:

    ```cmd
    mkdir marcnowa-flask-app
    cd marcnowa-flask-app
    py -3 -m venv .venv
    ```

### Activate the Environment

Activate the virtual environment to ensure you're working within the correct environment.

#### macOS/Linux

1. In your terminal, run:

    ```bash
    . .venv/bin/activate
    ```

#### Windows

1. In Command Prompt or PowerShell, run:

    ```cmd
    .venv\Scripts\activate
    ```

Your shell prompt will change to show the name of the activated environment.

### Install Packages

If you have a `requirements.txt` file that lists all necessary packages, you can use it to install the dependencies in your virtual environment.

1. Ensure that your virtual environment is activated.
2. Run the following command to install the packages listed in `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

### Install Flask

If you don’t have a `requirements.txt` file, you can manually install Flask by running:

```bash
pip install Flask
