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

# Helper function to extract plain text safely
def get_text(response):
    content = response.content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])
            elif isinstance(item, str):
                text_parts.append(item)
        return "".join(text_parts).strip()
    
    if isinstance(content, str):
        content = content.strip()
        if content.startswith("[{") and "'text':" in content:
            try:
                parsed = ast.literal_eval(content)
                return "".join(item.get("text", "") for item in parsed if isinstance(item, dict)).strip()
            except Exception:
                return content
        return content
    return str(content).strip()