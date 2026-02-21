import os
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv(r'C:\Users\SRJ\SRJ\Work\agentic_ai\.env')

gemini_api_key = os.getenv('GOOGLE_API_KEY')
openai = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

server_params = StdioServerParameters(
    command="uv",
    args=["C:\Users\SRJ\SRJ\Work\agentic_ai\ai-engineering-nexus\contract-engine\mcp\router.py"]
)

model="gemini-2.5-flash"

async def run_conversation(prompt):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = await session.list_tools()
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.args_schema
                    }
                } for t in mcp_tools.tools
            ]

            messages = [
                {
                    "role": "user",
                    "content": "prompt"
                }
            ]

            response = openai.chat.completions.create(
                model = model,
                messages = messages,
                tools = openai_tools
            )

            tool_call = response.choices[0].message.tool_calls[0]
            if(tool_call):
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"🛠️ LLM is calling tool: {name} with {args}")

                result = await session.call_tool(name = name, arguments = args)
                tool_result_text = result.content[0].text

                messages.append(response.choices[0].message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result_text
                })
                
                final_response = openai.chat.completions.create(
                    model=model,
                    messages=messages
                )
                
                return final_response.choices[0].message.content
            
if __name__ == "__main__":
    answer = asyncio.run(run_conversation("What is 144 divided by 12?"))
    print(f"🤖 AI Response: {answer}")
