from langchain_core.tools import tool
from database.vectordb_manager import get_similar_docs
from database.database_manager import DatabaseManager
from langchain_core.runnables import RunnableConfig

import datetime
from utils.utilities import convert_to_yyyy_mm_dd


@tool
def lookup_policy(query: str) -> str:
    """Consult the company policies to answer any query related to booking, cancellation, refund related queries
    related to flights, hotels, excursions or transport"""

    docs = get_similar_docs(query)
    return "\n\n".join([doc.page_content for doc in docs])


@tool
def fetch_user_flight_information(config: RunnableConfig):
    """
    Fetch all the information and details related to flight booked by the user

    :return: A list of dictionaries where each dictionary contains the ticket details,
            associated flight details, for each ticket belonging to the user.
    """

    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    if not passenger_id:
        raise ValueError("No passenger id configured")

    query = "SELECT * FROM flight_passengers WHERE"
    params = []
    limit = 10

    query += " passenger_id = %s"
    params.append(passenger_id)

    query += " LIMIT %s"
    params.append(limit)
    print(query)

    db_manager = DatabaseManager()
    results = db_manager.fetch_records_with_params(query, params)

    return results


@tool
def search_flights(source_city: str, destination_city: str, class_of_flight: str):
    """
    Search for flights based on source city, destination city and class of flight.
    :param source_city: Name of city from where the flight is going to depart.
    :param destination_city: Destination city where the flight is going to go.
    :param class_of_flight: Class of flight, could be either Economy or Business
    :return: Returns a list of dictionaries with information on flights.
    """

    if class_of_flight.title() not in ["Economy", "Business"]:
        raise ValueError("Class of flight can only be Economy or Business")

    query = "SELECT * FROM flights WHERE"
    params = []
    limit = 10

    query += " source_city = %s"
    params.append(source_city.title())

    query += " AND destination_city = %s"
    params.append(destination_city.title())

    query += " AND class = %s"
    params.append(class_of_flight.title())

    query += " LIMIT %s"
    params.append(limit)
    print(query)

    db_manager = DatabaseManager()
    results = db_manager.fetch_records_with_params(query, params)

    return results


def fetch_passenger_ticket(pnr_no: str, passenger_id: str):

    query = "SELECT * FROM flight_passengers WHERE"
    params = []
    limit = 1

    query += " passenger_id = %s"
    params.append(passenger_id)

    query += " AND pnr_no = %s"
    params.append(pnr_no)

    query += " LIMIT %s"
    params.append(limit)
    print(query)

    db_manager = DatabaseManager()
    results = db_manager.fetch_records_with_params(query, params)

    return results

@tool
def update_flight_to_new_flight(pnr_no: str, new_departure_date: str, travel_time: int, config: RunnableConfig):
    """
    This function updates the flight details like departure date for passenger.
    :param pnr_no: PNR number of the passenger travelling
    :param new_departure_date: The updated departure date on which the passenger wishes to travel now.
    :param travel_time: Time taken to complete the journey.
    :return: Returns successful message if the update operation is successful.
    """

    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)

    if not passenger_id:
        raise ValueError("No passenger id configured")

    results = fetch_passenger_ticket(pnr_no, passenger_id)

    if len(results) == 0:
        return "No records exists with this PNR."

    new_dot = convert_to_yyyy_mm_dd(new_departure_date)
    dot = datetime.datetime.strptime(new_dot, "%Y-%m-%d")
    new_doa = dot + datetime.timedelta(hours=travel_time)
    new_doa = datetime.datetime.strftime(new_doa, "%Y-%m-%d")

    query = "UPDATE flight_passengers SET"
    params = []

    query += " date_of_departure = %s"
    params.append(new_dot)

    query += ", date_of_arrival = %s"
    params.append(new_doa)

    query += " WHERE passenger_id = %s"
    params.append(passenger_id)

    query += " AND pnr_no = %s"
    params.append(pnr_no)

    print(query)
    db_manager = DatabaseManager()
    db_manager.execute_query(query, params)

    return "Record update successfully"


@tool
def cancel_flight_ticket(pnr_no: str, config: RunnableConfig):

    """
    This function is called when the passenger wants to cancel the flight ticket.
    :param pnr_no: PNR number to uniquely identify the ticket
    :return: Returns a successful message if the ticket is cancelled.
    """

    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)

    if not passenger_id:
        raise ValueError("No passenger id configured")

    results = fetch_passenger_ticket(pnr_no, passenger_id)

    if len(results) == 0:
        return "No records exists with this PNR."

    query = "DELETE from flight_passengers WHERE"
    params = []

    query += " passenger_id = %s"
    params.append(passenger_id)

    query += " AND pnr_no = %s"
    params.append(pnr_no)

    print(query)
    db_manager = DatabaseManager()
    db_manager.execute_query(query, params)

    return "Ticket cancelled successfully"

