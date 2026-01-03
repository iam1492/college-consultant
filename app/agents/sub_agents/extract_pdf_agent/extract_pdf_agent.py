
from google.adk.agents import Agent
from .tools.read_pdf import read_pdf
from .cds_schema import UniversityDataSchema
from google.adk.planners import BuiltInPlanner
from google.genai import types

def create_extract_pdf_agent():
    return Agent(
        name="extract_pdf_agent",
        model="gemini-3-flash-preview",
        instruction="""
        당신은 대학 입시 데이터 전문가입니다. 
        주어진 PDF 파일명을 도구(read_pdf)에 전달하여 내용을 읽고,
        JSON 스키마에 맞춰 데이터를 추출하세요.
        """,
        tools=[read_pdf],
        output_schema=UniversityDataSchema,
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_level=types.ThinkingLevel.HIGH,)
        ),
    )

extract_pdf_agent = create_extract_pdf_agent()