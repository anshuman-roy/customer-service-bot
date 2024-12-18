from langchain_core.tools import tool
from database.vectordb_manager import get_similar_docs
from database.database_manager import DatabaseManager
from langchain_core.runnables import RunnableConfig


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
