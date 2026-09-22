from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated

from langchain_core.messages import (
    BaseMessage,
    SystemMessage
)

from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages

from dotenv import load_dotenv

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_tavily import TavilySearch

from langchain_core.tools import tool

from langgraph.checkpoint.sqlite import SqliteSaver

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from langgraph.types import interrupt

import requests
import math
import os
import sqlite3


# =========================================================
# Load environment variables
# =========================================================

load_dotenv()


# =========================================================
# Initialize Groq LLM
# =========================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


# =========================================================
# Embedding model
# =========================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# =========================================================
# RAG DOCUMENT INGESTION
# =========================================================

def ingest_rag_document(file_path):

    DB_PATH = "faiss_db"

    loader = PyPDFLoader(file_path)

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    vector_store.save_local(DB_PATH)


# =========================================================
# Get RAG retriever
# =========================================================

def get_retriever():

    DB_PATH = "faiss_db"

    if not os.path.exists(DB_PATH):
        return None

    vector_store = FAISS.load_local(
        folder_path=DB_PATH,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    return retriever


    documents = retriever.invoke(query)

    if not documents:
        return "No relevant information was found in the PDF."

    formatted_documents = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        source = document.metadata.get(
            "source",
            "Unknown source"
        )

        page = document.metadata.get(
            "page",
            "Unknown page"
        )

        formatted_documents.append(
            f"Document: {index}\n"
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Content: {document.page_content}"
        )

    return "\n\n".join(formatted_documents)


# RAG Tool
@tool
def rag_tool(query: str) -> str:
    """
    Retrieve relevant information from the PDF documents.

    Use this tool when the user asks factual or conceptual questions
    that may be answered using the stored PDF documents.

    Args:
        query: The question or search query used to retrieve PDF content.
    """
    retriever = get_retriever()

    if retriever is None:
        return "No PDF has been uploaded yet. Please upload a document first."

    documents = retriever.invoke(query)

    if not documents:
        return "No relevant information was found in the PDF."

    formatted_documents = []

    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "Unknown source")
        page = document.metadata.get("page", "Unknown page")

        formatted_documents.append(
            f"Document: {index}\n"
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Content: {document.page_content}"
        )

    return "\n\n".join(formatted_documents)
# =========================================================
# WEB SEARCH TOOL
# =========================================================

search_tool = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="advanced"
)


# =========================================================
# CALCULATOR TOOL
# =========================================================

@tool
def calculator(expression: str) -> str:
    """
    Useful for simple math calculations.
    Input should be a valid math expression.
    Example: 2+2, math.sqrt(16), 10*5
    """
    try:
        allowed = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum
        }

        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)

    except Exception as e:
        return f"Calculation error: {str(e)}"



# =========================================================
# PURCHASE STOCK TOOL
# HUMAN-IN-THE-LOOP
# =========================================================

@tool
def purchase_stock(
    symbol: str,
    quantity: int
) -> dict:
    """
    Simulate purchasing a given quantity of a stock symbol.

    HUMAN-IN-THE-LOOP:
    Before confirming the purchase, this tool pauses
    the graph and waits for human approval.
    """

    # -----------------------------------------------------
    # INTERRUPT THE GRAPH
    # -----------------------------------------------------

    decision = interrupt(
        f"Approve buying {quantity} shares of "
        f"{symbol}? (yes/no)"
    )


    # -----------------------------------------------------
    # HUMAN APPROVED
    # -----------------------------------------------------

    if (
        isinstance(decision, str)
        and decision.lower().strip() == "yes"
    ):

        return {
            "status": "success",
            "message": (
                f"Purchase order placed for "
                f"{quantity} shares of {symbol}."
            ),
            "symbol": symbol,
            "quantity": quantity
        }
@tool
def get_weather(location: str) -> dict:
    """
    Get the current real-time weather for a location.
    """

    try:

        # -------------------------------------------------
        # Geocoding
        # -------------------------------------------------

        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )

        geo_params = {
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(
            geo_url,
            params=geo_params,
            timeout=10
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        if not geo_data.get("results"):

            return {
                "error": (
                    f"Location '{location}' not found."
                )
            }

        result = geo_data["results"][0]

        latitude = result["latitude"]
        longitude = result["longitude"]

        city = result.get(
            "name",
            location
        )

        country = result.get(
            "country",
            ""
        )

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "timezone": "auto"
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = weather_data["current"]


        return {
            "location": f"{city}, {country}",
            "temperature": (
                f"{current['temperature_2m']} °C"
            ),
            "feels_like": (
                f"{current['apparent_temperature']} °C"
            ),
            "humidity": (
                f"{current['relative_humidity_2m']}%"
            ),
            "precipitation": (
                f"{current['precipitation']} mm"
            ),
            "wind_speed": (
                f"{current['wind_speed_10m']} km/h"
            ),
            "weather_code": current["weather_code"],
            "time": current["time"]
        }

    except requests.RequestException as e:

        return {
            "error": f"Weather API error: {str(e)}"
        }

    except Exception as e:

        return {
            "error": f"Unexpected error: {str(e)}"
        }


# =========================================================
# TOOL LIST
# =========================================================

tools = [
    search_tool,
    calculator,
    purchase_stock,
    get_weather,
    rag_tool,

    # IMPORTANT:
    # purchase_stock MUST be included
    purchase_stock
]

# =========================================================
# Bind tools to LLM
# =========================================================

llm_with_tools = llm.bind_tools(tools)


# =========================================================
# Chat State
# =========================================================

class ChatState(TypedDict):

    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]


# =========================================================
# CHAT NODE
# =========================================================

def chat_node(state: ChatState):

    system_message = SystemMessage(
        content=(
            "You are a helpful Agentic Chatbot with "
            "access to several tools.\n\n"

            "Tool usage instructions:\n"

            "- Use 'rag_tool' for questions about "
            "the uploaded PDF or document. "
            "Always retrieve relevant document content "
            "before answering PDF-related questions.\n"

            "- Use 'search_tool' for current events, "
            "recent information, or information that "
            "requires an internet search.\n"

            "- Use 'calculator' for mathematical "
            "calculations.\n"

            "- Use 'get_stock_price' when the user asks "
            "for the current price of a stock.\n"

            "- Use 'get_weather' when the user asks "
            "about current weather for a location.\n"

            "- Use 'purchase_stock' when the user asks "
            "to purchase/buy shares of a stock. "
            "This action requires human approval before "
            "the purchase can be confirmed.\n\n"

            "Answer general questions directly when "
            "no tool is required.\n"

            "Do not invent information from the uploaded "
            "document.\n"

            "If the user asks about a PDF but no document "
            "is available, ask them to upload a PDF.\n"

            "After receiving a tool result, provide a "
            "clear and helpful final answer."
        )
    )


    # -----------------------------------------------------
    # Use the complete conversation history
    # This allows the LLM to use older messages restored
    # from the SQLite checkpoint for the current thread.
    # -----------------------------------------------------

    messages = [
        system_message,
        *state["messages"]
    ]
# -----------------------------------------------------
    # Call LLM
    # -----------------------------------------------------

    response = llm_with_tools.invoke(
        messages
    )


    return {
        "messages": [response]
    }


# =========================================================
# TOOL NODE
# =========================================================

tool_node = ToolNode(tools)


# =========================================================
# SQLITE CHECKPOINT
# =========================================================

conn = sqlite3.connect(
    database="chatbot.db",
    check_same_thread=False
)

checkpoint = SqliteSaver(conn)


# =========================================================
# BUILD GRAPH
# =========================================================

graph = StateGraph(ChatState)


graph.add_node(
    "chat_node",
    chat_node
)

graph.add_node(
    "tools",
    tool_node
)


graph.add_edge(
    START,
    "chat_node"
)

graph.add_conditional_edges(
    "chat_node",
    tools_condition
)

graph.add_edge(
    "tools",
    "chat_node"
)

# =========================================================
# COMPILE GRAPH
# =========================================================

chatbot = graph.compile(
    checkpointer=checkpoint
)


# =========================================================
# GET ALL THREADS
# =========================================================

def get_all_threads():

    all_threads = set()

    for ckpt in checkpoint.list(None):

        thread_id = (
            ckpt.config["configurable"]["thread_id"]
        )

        all_threads.add(thread_id)

    return list(all_threads)


