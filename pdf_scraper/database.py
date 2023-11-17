import pandas as pd
import pyodbc

def save_to_sql_server(pdf_metadata_list):
    # Create a pandas DataFrame from the list of dictionaries
    df = pd.DataFrame(pdf_metadata_list)

    # Connect to the SQL Server database
    # connection_string = "DRIVER={SQL Server};SERVER=HP\\SQLEXPRESS;DATABASE=your_database;UID=your_username;PWD=your_password"
    connection_string = "DRIVER={SQL Server};SERVER=HP\\SQLEXPRESS;DATABASE=Product;Trusted_Connection=yes"
    connection = pyodbc.connect(connection_string)

    try:
        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        # Iterate over the list of dictionaries and insert data into the table
        for metadata in pdf_metadata_list:
            # Customize this INSERT statement based on your table structure
            insert_query = f"INSERT INTO pdf_metadata (url, title) VALUES (?, ?)"
            cursor.execute(insert_query, metadata['url'], metadata['title'])

        # Commit the changes to the database
        connection.commit()

    except Exception as e:
        # Handle exceptions, if any
        print(f"Error while inserting data into the database: {e}")

    finally:
        # Close the cursor and the database connection
        cursor.close()
        connection.close()  