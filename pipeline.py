import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
import ast

# Load environment variables
load_dotenv()

# Define the State for our sequential pipeline
class CodeState(TypedDict):
    raw_code: str
    audit_report: str
    optimized_code: str
    documentation: str


# Initialize the Gemini Model
llm = ChatGoogleGenerativeAI(
    model="gemini-3.7-flash", 
    temperature=0.2 
)