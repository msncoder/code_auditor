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


# Clean code block markdown tags
def clean_code_block(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if len(lines) > 1 and lines[0].startswith("```"):
            lines = lines[1:]
        if len(lines) > 0 and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text


# --- Agent Node 1: Scanner ---
def scanner_node(state: CodeState) -> dict:
    prompt = (
        "You are an expert Security & QA Engineer. Analyze the following code for bugs, "
        "security vulnerabilities, anti-patterns, and bad practices. "
        "Be concise and output the issues in a clear bulleted list.\n\n"
        f"Code to analyze:\n{state['raw_code']}"
    )
    response = llm.invoke(prompt)
    return {"audit_report": get_text(response)}


# --- Agent Node 2: Refactor & Optimizer ---
def refactor_node(state: CodeState) -> dict:
    prompt = (
        "You are an elite Senior Backend Developer. Based on the following Audit Report, "
        "refactor and optimize the original code. Ensure it follows best practices (like PEP8 for Python), "
        "is highly performant, and secure. Return ONLY the refactored code without any explanations.\n\n"
        f"Audit Report:\n{state['audit_report']}\n\n"
        f"Original Code:\n{state['raw_code']}"
    )
    response = llm.invoke(prompt)
    return {"optimized_code": clean_code_block(get_text(response))}