import os
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
import uuid
import json
from models import TaskBreakdown, ToolCall
import asyncio

load_dotenv(r'C:\Users\SRJ\SRJ\Work\agentic_ai\.env')

gemini_api_key = os.getenv('GOOGLE_API_KEY')

openai = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model="gemini-2.5-flash"

async def task_breakdown():
    response = await openai.beta.chat.completions.parse(
        model=model,
        messages=[
            {   "role": "system",
                "content": "You are a helpful assistant. You will be given some task."
                "You have to breakdown that task and return in the specified format only."
            },
            {
                "role": "user",
                "content": "Number of ways to climb stairs if we can go up 1 or 2"
                "step at a time and there are 30 steps."
            }
        ],
        response_format = TaskBreakdown
    )
    print(response.choices[0].message.parsed)

async def tool_call():
    response = await openai.beta.chat.completions.parse(
        model=model,
        messages=[
            {   "role": "system",
                "content": "You are a helpful assistant. You will be given some task."
                "You have to find out which tools will be required for that task and"
                "return in the specified format only. The tools which have been given to"
                "you are add, subtract, multiply and divide."
            },
            {
                "role": "user",
                "content": "LCM of 20 and 26"
            }
        ],
        response_format = ToolCall
    )
    print(response.choices[0].message.parsed)

if __name__ == "__main__":
    asyncio.run(tool_call())
