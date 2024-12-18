import uuid
from src.graph import Workflow
from utils.utilities import print_event


thread_id = str(uuid.uuid4())

config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information
        "passenger_id": 51495,
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}


if __name__ == "__main__":

    _printed = set()
    workflow = Workflow()

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        events = workflow.graph.stream(
            {"messages": ("user", user_input)}, config, stream_mode="values"
        )
        for e in events:
            print_event(e, _printed)
