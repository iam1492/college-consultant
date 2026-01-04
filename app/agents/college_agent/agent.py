"""
College Agent ADK App Entry Point with Sequential Pipeline.

This file registers the college consulting service as a SequentialAgent.
Pipeline: query_analysis_agent -> college_agent

1. query_analysis_agent: Analyzes user query, translates to English, optimizes for RAG
2. college_agent: Uses optimized query to search Pinecone and provide answers

NOTE: ADK requires the agent variable to be named 'root_agent' for discovery.
"""

from google.adk.agents import SequentialAgent
from app.agents.sub_agents.query_analysis_agent.query_analysis_agent import (
    create_query_analysis_agent,
)
from app.agents.sub_agents.college_agent.college_agent import create_college_agent


def create_college_consulting_pipeline() -> SequentialAgent:
    """
    Create the college consulting sequential pipeline.
    
    The pipeline consists of:
    1. query_analysis_agent: Analyzes and translates user query to optimized English
       - Output stored in 'query_analysis_result' via output_key
    2. college_agent: Uses {query_analysis_result} to search Pinecone and respond
    
    Returns:
        SequentialAgent: A sequential pipeline for college consulting.
    """
    return SequentialAgent(
        name="college_consulting_pipeline",
        description="A sequential pipeline for college consulting that first analyzes the query and then searches for relevant information.",
        sub_agents=[
            create_query_analysis_agent(),  # First: analyze and translate query
            create_college_agent(),         # Second: search and respond
        ],
    )


# ADK requires this variable to be named 'root_agent'
root_agent = create_college_consulting_pipeline()
