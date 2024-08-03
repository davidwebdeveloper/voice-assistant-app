import pandas as pd
import mysql.connector
from mysql.connector import Error

db_host = 'localhost'
db_user = 'root'
db_password = 'root@123'
db_name = 'world_cities'

def read_csv(file_path):
    """
    Reads a CSV file into a pandas DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Data loaded from {file_path}")
        return df
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except pd.errors.EmptyDataError:
        print("Error: No data found in the file.")
    except pd.errors.ParserError:
        print("Error: Data parsing error.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return None

def connect_to_mysql(host, user, password, database):
    """
    Connects to the MySQL database.
    """
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            print("Successfully connected to MySQL")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return None

def create_table_if_not_exists(connection):
    """
    Creates the world_cities table if it does not exist.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS world_cities (
        id INT PRIMARY KEY,
        city_ascii VARCHAR(255) NOT NULL,
        latitude FLOAT,
        longitude FLOAT,
        country VARCHAR(255),
        iso2 CHAR(2),
        iso3 CHAR(3),
        admin_name VARCHAR(255),
        capital VARCHAR(255),
        population INT
    )
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'world_cities' created or already exists.")
    except Error as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()

def clean_data(df):
    """
    Cleans the DataFrame by handling NaN values and other issues.
    """
    try:
        # Replace NaN with default values or empty strings
        df = df.fillna({
            'city_ascii': '',
            'capital': '',
            'population': 0  # Default value for missing population
        })
        
        # Convert 'population' and 'id' to integers
        df['population'] = df['population'].astype(int)
        df['id'] = df['id'].astype(int)
        
        # Ensure no NaN values remain
        df = df.dropna()
        
        print("Data cleaned successfully.")
        return df
    except KeyError as e:
        print(f"Error: Missing column in DataFrame - {e}")
    except ValueError as e:
        print(f"Error: Data type conversion issue - {e}")
    except Exception as e:
        print(f"Error cleaning data: {e}")
    return df

def validate_data(df):
    """
    Validates the DataFrame to ensure data consistency.
    """
    try:
        print("Data validation:")
        print(df.dtypes)
        print(df.head())
    except Exception as e:
        print(f"Error during data validation: {e}")

def fetch_indian_cities_from_db():
    """
    Fetches Indian cities from the MySQL database.
    
    Returns:
    dict: A dictionary mapping city names in lowercase to their proper names.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root@123',
            database='world_cities'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT city_ascii FROM world_cities WHERE country = 'India'")
            cities = {row[0].lower(): row[0] for row in cursor.fetchall()}
            return cities
    except Error as e:
        print(f"Error fetching cities from database: {e}")
        return {}
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_data_from_dataframe(df, connection):
    """
    Inserts data from a DataFrame into the MySQL table.
    """
    insert_query = """
    INSERT INTO world_cities (id, city_ascii, latitude, longitude, country, iso2, iso3, admin_name, capital, population)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data_tuples = [tuple(x) for x in df[['id', 'city_ascii', 'lat', 'lng', 'country', 'iso2', 'iso3', 'admin_name', 'capital', 'population']].to_numpy()]
    
    try:
        cursor = connection.cursor()
        cursor.executemany(insert_query, data_tuples)
        connection.commit()
        print(f"{cursor.rowcount} records inserted successfully.")
    except Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()  # Rollback the transaction if there's an error
    except Exception as e:
        print(f"Unexpected error during data insertion: {e}")
        connection.rollback()  # Rollback the transaction if there's an unexpected error
    finally:
        cursor.close()

def store_world_cities():
    """
    Reads the world cities CSV file, cleans the data, and stores it in the MySQL database.
    """
    file_path = 'src/files/worldcities.csv'
    # Read CSV file
    df = read_csv(file_path)
    if df is not None:
        # Clean and validate data
        df = clean_data(df)
        validate_data(df)
        
        # Connect to MySQL
        connection = connect_to_mysql(db_host, db_user, db_password, db_name)
        if connection is not None:
            # Create table if not exists
            create_table_if_not_exists(connection)
            # Insert data into MySQL
            insert_data_from_dataframe(df, connection)
            # Close the connection
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    store_world_cities()
