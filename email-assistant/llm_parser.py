import os
import google.generativeai as genai
from pydantic import BaseModel, Field

class AgentIntent(BaseModel):
    agent: str = Field(description="The agent to use: 'organizer' (for moving/labeling emails) or 'cleaner' (for deleting emails)")
    gmail_query: str = Field(description="The standard Gmail search query string to find matching emails (e.g., 'subject:flight OR from:airline')")
    label: str | None = Field(default=None, description="The name of the label/folder to create and apply (only for 'organizer' agent)")

def parse_user_query(user_query: str) -> AgentIntent:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    system_instruction = """
    You translate natural language requests for organizing or cleaning Gmail into a structured JSON intent.
    Return ONLY JSON matching this exact structure:
    - "agent": string, either "organizer" (move/label emails) OR "cleaner" (delete emails)
    - "gmail_query": string, a standard Gmail search query (e.g., "subject:flight OR from:airline")
    - "label": string, the name of the folder/label (only if agent is organizer, otherwise null)
    """

    # Using gemini-2.5-flash as it is extremely fast, capable, and free
    model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_instruction)
    
    response = model.generate_content(
        user_query,
        generation_config=genai.GenerationConfig(response_mime_type="application/json")
    )
    
    return AgentIntent.model_validate_json(response.text)
