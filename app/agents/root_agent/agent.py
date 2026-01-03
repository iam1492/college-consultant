from google.adk.agents import Agent, SequentialAgent
# Use absolute import assuming run from project root
from app.sub_agents.extract_pdf_agent.extract_pdf_agent import create_extract_pdf_agent

root_agent = SequentialAgent(
        name="root_agent",
        description="Root agent",
        sub_agents=[create_extract_pdf_agent()]
    )


