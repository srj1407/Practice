import os
from pydantic import ValidationError
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
import uuid
import json
from models import TaskBreakdown, ToolCall
import asyncio
import re
from difflib import get_close_matches
from datetime import datetime

load_dotenv(r'C:\Users\SRJ\SRJ\Work\agentic_ai\.env')

gemini_api_key = os.getenv('GOOGLE_API_KEY')

openai = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model="gemini-2.5-flash"

async def tool_call(prompt):
    print(f'\nInside tool_call method')
    response = await openai.chat.completions.create(
        model=model,
        messages=prompt,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def extract_json_from_text(prompt):
    print(f'\nInside extract_Json_from_text method')
    match = re.search(r'\{.*\}', prompt, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return None
    return None

async def ask_llm_to_fix(prompt, response, e):
    print(f'\nInside ask_llm_to_fix method')
    response = await openai.chat.completions.create(
        model=model,
        messages=[
            {   "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": f"""Your previous response to my query was not in proper
                format and failed to validate. Please check and respond in proper
                format.

                Original Query : 

                {prompt}

                Your Response : 

                {response}

                Error : 

                {e}

                Please fix it and return valid JSON matching this schema:

                {ToolCall.model_json_schema()}
                """
            }
        ]
    )
    return response.choices[0].message.content

def fallback_parse(response):
    print(f'\nInside fallback_parse method')
    try:
        data = json.loads(response)
        if 'tool_name' in data:
            return {'tool_name': data['tool_name'], 'parameters': {}}
    except:
        if 'add' in response.lower():
            return {"tool_name": "add", "parameters": {}}
        if 'subtract' in response.lower():
            return {"tool_name": "subtract", "parameters": {}}
        if 'multiply' in response.lower():
            return {"tool_name": "multiply", "parameters": {}}
        if 'divide' in response.lower():
            return {"tool_name": "divide", "parameters": {}}

def fix_tool_name(name, VALID_TOOLS):
    print(f'\nInside fix_tool_name method')
    matches = get_close_matches(name, VALID_TOOLS, n=1)
    return matches[0] if matches else name

async def log_failure(prompt, response, error):
    print(f'\nInside log_failure method')
    failure = {
        "timestamp": datetime.now().isoformat(),
        'prompt': prompt,
        'response': response,
        'error': error
    }

    with open('failures.json', 'a') as f:
        f.write(json.dumps(failure) + '\n')

async def robust_parser(prompt):
    print(f'\nInside robust_parser method')
    response = await tool_call(prompt)
    
    try:
        return ToolCall.model_validate(response)
    except ValidationError as e:
        print(f'\nException after first validation check: \n{e}')
        cleaned = extract_json_from_text(response)
        if cleaned:
            print(f'\n{cleaned}')
            try:
                print(f'After cleaned \n{ToolCall.model_validate(cleaned)}')
                return ToolCall.model_validate(cleaned)
            except Exception as e:
                print(f'\nException after cleaning: \n{e}')
                pass
    
        for i in range(2):
            response = await ask_llm_to_fix(prompt, response, e)
            cleaned = extract_json_from_text(response)
            print(f'\n\nResult from ask_llm_to_fix[{i}]:\n\n{response}')
            try:
                return ToolCall.model_validate(cleaned)
            except Exception as e:
                print(f'\nException after ask_llm_to_fix method {i+1} time: \n{e}')
                continue

        partial = fallback_parse(response)
        if partial:
            VALID_TOOLS = ["add", "subtract", "multiply", "divide"]
            tool_name = partial.get("tool_name")
            if tool_name not in VALID_TOOLS:
                partial["tool_name"] = fix_tool_name(tool_name, VALID_TOOLS)
            return partial

        await log_failure(prompt, response, str(e))
        raise RuntimeError('Could not parse after all attempts.')

if __name__ == '__main__':
    prompt = [
        {   "role": "system",
            "content": f"""You are a helpful assistant. You will be given some task.
            You have to find out which tools will be required for that task and
            return as json output. I will give you a specific format.
            But the json output you give, you have to malform it somewhat 
            so that I can apply some clean method on it. The tools which
            have been given to you are add, subtract, multiply and divide.

            Format:

            {ToolCall.model_json_schema()}
            """
        },
        {
            "role": "user",
            "content": "LCM of 20 and 26"
        }
    ]
    response = asyncio.run(robust_parser(prompt))
    print(f'\nFinal Response: \n{response}')