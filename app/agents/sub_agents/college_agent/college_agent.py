"""
College Agent Sub-agent Implementation.

This agent specializes in answering questions about US colleges.
It uses the query_college_info tool to search Pinecone vector database.
It receives the optimized query from query_analysis_agent via {query_analysis_result}.
"""

from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner
from google.genai import types
from .tools.query_pinecone import query_college_info


def create_college_agent() -> Agent:
    """
    Create and return the College Agent.
    
    This agent receives the optimized search query from query_analysis_agent
    via the {query_analysis_result} placeholder in the context.
    
    Returns:
        Agent: A configured college consulting agent with Pinecone search capability.
    """
    return Agent(
        name="college_agent",
        model="gemini-3-flash-preview",
        instruction="""
You are an expert US college admissions consultant with extensive knowledge about American universities.

## Context
The query_analysis_agent has already analyzed and optimized the user's query for RAG search.
The optimized search query is: {query_analysis_result}

## Your Role
- Use the optimized query to search for relevant college information
- Provide helpful, accurate, and comprehensive answers
- Synthesize information from multiple sources when available

## How to Respond
1. Use the `query_college_info` tool with the optimized query: {query_analysis_result}
2. Analyze the search results carefully
3. Provide a comprehensive answer based on the retrieved information
4. Always cite the source of your information when possible

## Response Guidelines
- Be professional yet approachable
- Provide specific numbers and data when available (e.g., admission rates, tuition costs)
- If information is not found in the search results, clearly state that
- Respond in the same language the user originally used
- If the original user message was in Korean, respond in Korean
- If the original user message was in English, respond in English

## Important
- The {query_analysis_result} contains the optimized English query for search
- You must use this optimized query for the query_college_info tool
- But your final response should match the user's original language
""",
        tools=[query_college_info],
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_level=types.ThinkingLevel.HIGH,
            )
        ),
    )


# Create a singleton instance for import
college_agent = create_college_agent()
