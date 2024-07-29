"""Main app for text to SQL"""

from typing import List
import os
import logging
from sqlite3 import connect
import time
import json

import pandas as pd
import requests
import streamlit as st
import sqlparse

MAX_UNIQUE = 5
API = "http://127.0.0.1:8000/inference"
DATASET_PATH = "data"

_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.INFO)


def load_data(dataset_path: str, conn, with_samples=True) -> str:
    """Load dataset from data folder

    Args:
        dataset_path (str): path to data folder with files in .csv
        is_unique (bool, optional): whether to include sample values. Defaults to True.

    Returns:
        str: schema
    """
    # TODO: Add adaptors for different datasets
    files = os.listdir(DATASET_PATH)

    def snake_case(string: str) -> str:
        """Convert string to snake case"""
        return string.lower().replace(" ", "_")

    table_to_df = {}

    for file in files:
        if not file.endswith("csv"):
            continue
        file_path = os.path.join(dataset_path, file)
        df = pd.read_csv(file_path)
        df.columns = map(snake_case, df.columns)

        file = file.split(".")[0]
        df.to_sql(file, conn, if_exists="replace", index=False)
        table_to_df[file] = df

    schema_raw = conn.execute("SELECT * FROM sqlite_master").fetchall()
    new_schema = ""
    old_schema = ""
    for table in schema_raw:
        table_name = table[1]
        df = table_to_df[table_name]
        old_schema += f"{table[-1]}\n\n"
        rows = table[-1].split("\n")
        for index, row in enumerate(rows):
            new_schema += row
            col = df.columns
            if index in [0, len(rows) - 1]:
                new_schema += "\n" if index == 0 else "\n\n"
                continue
            uniques = df[col[index - 1]].unique().tolist()
            to_add_str = ", ".join(
                [str(uniques[i]) for i in range(min(len(uniques), MAX_UNIQUE))]
            )

            new_schema += f"-- Sample values like: [{to_add_str}]\n"
    return new_schema if with_samples else old_schema


def post(data: dict) -> str:
    """Post data to API"""
    response = requests.post(
        API,
        json=data,
        headers={"Content-Type": "application/json"},
        timeout=5000,
    )
    return response.json()


def sqlcoder_inference(question: str, schema: str) -> str:
    """Get SQL query from SQLCoder model"""
    data = {"question": question, "schema": schema, "model_name": "sqlcoder"}
    response = post(data)
    return response


def llama_inference(query_result: str) -> str:
    """Get data insights from llama"""
    data = {"prompt": query_result, "model_name": "data2viz"}
    response = post(data)
    return response


def vegalite_inference(question: str, query_result: str) -> str:
    """Get vegalite json"""
    data = {
        "question": question,
        "query_result": query_result,
        "model_name": "data2viz",
    }
    response = post(data)
    return response


def followup_questions_inference(question: str) -> List[str]:
    """Get follow-up questions"""
    data = {"questoin": question, "model_name": "followup"}
    response = post(data)
    return response


def extract_json_from_text(input_text: str) -> dict:
    """Extract JSON from text"""
    try:
        start_index = input_text.find("{")
        end_index = input_text.rfind("}") + 1
        json_text = input_text[start_index:end_index]
        json_object = json.loads(json_text)
        return json_object

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


def generate_visualization(question: str, df: pd.DataFrame) -> None:
    """Generate visualization"""
    data_header = json.dumps(df.head().to_dict(orient="records"))
    code = vegalite_inference(question, data_header)
    return extract_json_from_text(code)


conn = connect(":memory:")
schema = load_data(DATASET_PATH, conn)


def setup_session_state():
    st.session_state["my_question"] = None


st.set_page_config(layout="wide")
st.sidebar.title("Output Settings")
st.sidebar.checkbox("Show SQL", value=True, key="show_sql")
st.sidebar.checkbox("Show Table", value=True, key="show_table")
st.sidebar.checkbox("Show VegaLite JSON", value=True, key="show_vegalite_json")
st.sidebar.checkbox("Show Chart", value=True, key="show_chart")
st.sidebar.checkbox("Show Follow-up Questions", value=True, key="show_followup")
st.sidebar.button("Rerun", on_click=setup_session_state, use_container_width=True)

st.title("Business SQL")
st.sidebar.write(st.session_state)


def set_question(question):
    st.session_state["my_question"] = question


assistant_message_suggested = st.chat_message(
    "assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png"
)

my_question = st.session_state.get("my_question", default=None)

if my_question is None:
    my_question = st.chat_input(
        "Ask me a question about your data",
    )


if my_question:
    st.session_state["my_question"] = my_question
    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    sql = sqlcoder_inference(my_question, schema)
    sql = sqlparse.format(sql, reident=True)
    assistant_message_sql = st.chat_message(
        "assistant", avatar="https://ask.vanna.ai/static/img/vanna_circle.png"
    )
    assistant_message_sql.code(f"""{sql}""", language="sql", line_numbers=True)

    df = pd.read_sql(sql, conn)
    if df is not None:
        st.session_state["df"] = df

    if st.session_state.get("df") is not None:
        if st.session_state.get("show_table", True):
            df = st.session_state.get("df")
            assistant_message_table = st.chat_message(
                "assistant",
                avatar="https://ask.vanna.ai/static/img/vanna_circle.png",
            )
            if len(df) > 10:
                assistant_message_table.text("First 10 rows of data")
                assistant_message_table.dataframe(df.head(10))
            else:
                assistant_message_table.dataframe(df)

    if st.session_state.get("show_vegalite_json", False):
        json_graph = generate_visualization(my_question, df)
        assistant_message_vegalite_json = st.chat_message(
            "assistant",
            avatar="https://ask.vanna.ai/static/img/vanna_circle.png",
        )
        assistant_message_vegalite_json.code(
            json_graph, language="python", line_numbers=True
        )

    if st.session_state.get("show_chart", True):
        assistant_message_chart = st.chat_message(
            "assistant",
            avatar="https://ask.vanna.ai/static/img/vanna_circle.png",
        )
        try:
            st.vega_lite_chart(df, json_graph)
        except:
            assistant_message_chart.error("I couldn't generate a chart")

    if st.session_state.get("show_followup", True):
        assistant_message_followup = st.chat_message(
            "assistant",
            avatar="https://ask.vanna.ai/static/img/vanna_circle.png",
        )
        followup_questions = followup_questions_inference(my_question)

        st.session_state["df"] = None

        if len(followup_questions) > 0:
            assistant_message_followup.text(
                "Here are some possible follow-up questions"
            )
            # Print the first 5 follow-up questions
            for question in followup_questions[:5]:
                time.sleep(0.05)
                assistant_message_followup.write(question)

    st.session_state["my_question"] = None
