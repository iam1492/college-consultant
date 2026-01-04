"""
Query Analysis Agent Sub-agent Implementation.

This agent analyzes user queries and translates/optimizes them for RAG search.
It runs before college_agent in the sequential pipeline.
"""

from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner
from google.genai import types


def create_query_analysis_agent() -> Agent:
    """
    Create and return the Query Analysis Agent.
    
    This agent is responsible for:
    1. Analyzing the user's query (in any language)
    2. Translating it to English if needed
    3. Optimizing it for effective RAG vector search
    
    Returns:
        Agent: A configured query analysis agent.
    """
    return Agent(
        name="query_analysis_agent",
        model="gemini-3-flash-preview",
        instruction="""
You are a query analysis expert specializing in preparing user queries for RAG (Retrieval Augmented Generation) search.

## Your Role
Analyze the user's query about US colleges and universities, then produce an optimized English search query.

## Your Tasks
1. **Understand Intent**: Identify what specific information the user is asking for
2. **Translate to English**: If the query is in another language (e.g., Korean, Chinese), translate it to English
3. **Optimize for Search**: Rewrite the query to be more effective for semantic vector search
   - Extract key entities (college names, specific metrics)
   - Include relevant synonyms or related terms
   - Remove unnecessary filler words
   - Structure for maximum retrieval accuracy

## Output Format
Return ONLY the optimized English search query. Do not include explanations or additional text.

## Examples

Input: "해밀턴 대학교의 유학생 비율은?"
Output: "Hamilton College international student ratio percentage enrollment statistics"

Input: "하버드 학비 얼마야?"
Output: "Harvard University tuition fees cost of attendance annual expenses"

Input: "What's Stanford's acceptance rate?"
Output: "Stanford University admission acceptance rate selectivity statistics"

Input: "윌리엄스 칼리지 입학 마감일"
Output: "Williams College application deadline admission dates early decision regular decision"
""",
        output_key="query_analysis_result",
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_level=types.ThinkingLevel.HIGH,
            )
        ),
    )


# Create a singleton instance for import
query_analysis_agent = create_query_analysis_agent()
