from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
from src.agents import State, Assistant, assistant_runnable, tools_list
from utils.utilities import create_tool_node_with_fallback


class Workflow():

    def __init__(self):
        builder = StateGraph(State)

        # Define nodes: these do the work
        builder.add_node("assistant", Assistant(assistant_runnable))
        builder.add_node("tools", create_tool_node_with_fallback(tools_list))

        # Define edges: these determine how the control flow moves
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges(
            "assistant",
            tools_condition,
        )
        builder.add_edge("tools", "assistant")

        # The checkpointer lets the graph persist its state
        # this is a complete memory for the entire graph.
        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory)