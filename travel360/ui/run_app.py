import streamlit as st
from src.graph import Workflow
from textwrap import dedent
from langchain_core.messages import ToolMessage
import uuid

id1 = str(uuid.uuid4())
id2 = str(uuid.uuid4())


def run_app(config: dict, workflow: Workflow):

    st.title("Customer Service Bot")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant",
                                         "content": "How can I help you?",
                                        }]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input(key=id1):

        st.session_state.messages.append({"role": "user",
                                          "content": user_input,
                                          })
        st.chat_message("user").write(user_input)
        print("Session state: ", st.session_state.graph_snapshot.next)

        if user_input.lower() in ["quit", "exit", "q"]:
            msg = "Goodbye!"
            st.session_state.messages.append({"role": "assistant",
                                              "content": msg})
            st.chat_message("assistant").write(msg)
            st.info("Closing the session")
            st.stop()

        main_event = workflow.graph.invoke(
            {"messages": ("user", user_input)},
            config,
            stream_mode="values",
        )
        msg = main_event.get("messages")[-1].content

        st.session_state.messages.append({"role": "assistant",
                                          "content": msg,
                                          })
        st.chat_message("assistant").write(msg)

