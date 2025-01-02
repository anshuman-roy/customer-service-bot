import pandas as pd
import pymysql
from dotenv import load_dotenv
import os
from textwrap import dedent


load_dotenv()


class DatabaseManager():

    def __init__(self):
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_HOST_URL = os.getenv("DB_HOST_URL")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_USERNAME = os.getenv("DB_USERNAME")

    def get_db_connection(self):
        timeout = 100
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=timeout,
            cursorclass=pymysql.cursors.DictCursor,
            db=self.DB_NAME,
            host=self.DB_HOST_URL,
            password=self.DB_PASSWORD,
            read_timeout=timeout,
            port=15349,
            user=self.DB_USERNAME,
            write_timeout=timeout,
        )

        return connection

    def create_table(self, table_name: str):

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            create_table_query = ""

            if table_name == "hotel":
                create_table_query = dedent(text=f"""
                CREATE TABLE hotel (hotel_name VARCHAR(256) PRIMARY KEY, location VARCHAR(256), type_of_room 
                VARCHAR(256), capacity INTEGER, price INTEGER, is_available VARCHAR(3))
                """)
            if table_name == "flights":
                create_table_query = dedent(text=f"""
                CREATE TABLE flights (airline_name VARCHAR(256) PRIMARY KEY, source VARCHAR(256),
                destination VARCHAR(256), class VARCHAR(256), cost INTEGER,
                layover VARCHAR(256), travel_time FLOAT)
                """)
            if table_name == "flight_passengers":
                create_table_query = dedent(text=f"""
                CREATE TABLE flight_passengers (passenger_id INTEGER PRIMARY KEY,
                                                pnr_no VARCHAR(10),
                                                passenger_name VARCHAR(256),
                                                airline_name VARCHAR(256),
                                                date_of_departure DATE,
                                                date_of_arrival DATE,
                                                departure_city VARCHAR(256),
                                                arrival_city VARCHAR(256),
                                                no_of_passengers INTEGER,
                                                cost_of_flight FLOAT
                                                )
                """)

            cursor.execute(create_table_query)
            cursor.execute(dedent(text=f"""
            SELECT * FROM {table_name}
            """))
            print(cursor.fetchall())
        finally:
            connection.close()

    def upload_csv_to_db(self, csv_file_path: str, table_name: str):

        df = pd.read_csv(csv_file_path)
        values = [tuple(x) for x in df.values]

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()

            insert_stmt = ""
            if table_name == "hotel":
                insert_stmt = ("INSERT INTO hotel (id,hotel_name,location_country,location_city,"
                               "type_of_room,capacity,price,is_available) VALUES ({placeholders})").format(
                    placeholders=','.join(['%s'] * 8))
            if table_name == "flights":
                insert_stmt = ("INSERT INTO flights (airline_number,airline_name,source_country,"
                               "destination_country,class,cost,layover_country,travel_time,"
                               "source_city,destination_city,layover_city) VALUES ({placeholders})").format(
                    placeholders=','.join(['%s'] * 11))
            if table_name == "transport":
                insert_stmt = ("INSERT INTO transport (id,travel_agency_name,cab_type,location_country,"
                               "location_city,cost) VALUES ({placeholders})").format(
                    placeholders=','.join(['%s'] * 6))
            if table_name == "flight_passengers":
                insert_stmt = ("INSERT INTO flight_passengers (passenger_id, pnr_no, passenger_name, airline_name,"
                               "date_of_departure,	date_of_arrival, departure_city, arrival_city,	no_of_passengers,"
                               "cost_of_flight) VALUES ({placeholders})").format(
                    placeholders=','.join(['%s'] * 10)
                )

            cursor.executemany(query=insert_stmt, args=values)
            cursor.connection.commit()
        except Exception as e:
            print(e)
        finally:
            connection.close()

    def fetch_records(self, query):

        try:
            connection = self.get_db_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
        finally:
            connection.close()

        return results

    def fetch_records_with_params(self, query, params):

        try:
            connections = self.get_db_connection()
            cursor = connections.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            print("Records fetched:", len(rows))

        finally:
            cursor.close()
            connections.close()

        return rows

    def execute_query(self, query: str, params: list):

        try:
            connections = self.get_db_connection()
            cursor = connections.cursor()
            cursor.execute(query, params)
            connections.commit()

        finally:
            cursor.close()
            connections.close()




if __name__ == "__main__":

    db_manager = DatabaseManager()

    # db_manager.create_table(table_name="flight_passengers")
    db_manager.upload_csv_to_db(csv_file_path="/Users/anshuman.roy/Downloads/passenger_flight_details_updated.csv",
                                table_name="flight_passengers")
    # print(db_manager.fetch_records(query="SELECT * from flights"))
