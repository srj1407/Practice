import os
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
import json
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

load_dotenv(r'C:\Users\SRJ\SRJ\Work\agentic_ai\.env')

gemini_api_key = os.getenv('GOOGLE_API_KEY')
openai = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model="gemini-2.5-flash"

url = "http://localhost:8000/mcp"

async def run_conversation(prompt):
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = await session.list_tools()
            print(mcp_tools)
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description or "",
                        "parameters": (
                            getattr(t, "inputSchema", None)
                            or getattr(t, "input_schema", None)
                            or {"type": "object", "properties": {}}
                        ),
                    }
                } for t in mcp_tools.tools
            ]

            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            response = await openai.chat.completions.create(
                model = model,
                messages = messages,
                tools = openai_tools
            )
            print(f'First response: {response}')
            tool_calls = response.choices[0].message.tool_calls or []
            if not tool_calls:
                return response.choices[0].message.content

            tool_call = tool_calls[0]
            if(tool_call):
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"🛠️ LLM is calling tool: {name} with {args}")

                result = await session.call_tool(name = name, arguments = args)
                tool_result_text = result.content[0].text
                print(f'tool_result_text:\n{tool_result_text}')

                messages.append(response.choices[0].message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result_text
                })
                
                final_response = await openai.chat.completions.create(
                    model=model,
                    messages=messages
                )
                
                return final_response.choices[0].message.content
            
if __name__ == "__main__":
    answer = asyncio.run(run_conversation("What is the current weather of Samastipur?"))
    print(f"🤖 AI Response: {answer}")
