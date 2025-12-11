import os
import json
from openai import OpenAI
from tools import (
    TOOLS_SCHEMA, 
    CURRENT_TIME_REF, 
    check_schedule, 
    get_next_meeting_with, 
    block_time_slot
)
from dotenv import load_dotenv
load_dotenv()

# Initialize Client
client = OpenAI()

# Map string names to actual functions
AVAILABLE_FUNCTIONS = {
    "check_schedule": check_schedule,
    "get_next_meeting_with": get_next_meeting_with,
    "block_time_slot": block_time_slot
}

def run_calendar_agent(user_query: str):
    """
    Main entry point for the LLM Agent.
    1. Sends query to LLM.
    2. Checks if LLM wants to call a tool.
    3. Executes tool and sends result back to LLM.
    4. Returns final response.
    """
    
    # System prompt to ground the LLM in the "Current Time"
    messages = [
        {
            "role": "system",
            "content": (
                f"You are a calendar assistant. Current time: {CURRENT_TIME_REF.isoformat()}. "
                "Assume the year is 2025. "
                "When blocking time, ensure start_time < end_time. "
                "Always use ISO 8601 format for tool arguments."
            )
        },
        {"role": "user", "content": user_query}
    ]

    # 1. First API Call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto"
    )

    response_msg = response.choices[0].message
    tool_calls = response_msg.tool_calls

    # 2. Check if tool was called
    while True:
        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )

        response_msg = response.choices[0].message
        tool_calls = response_msg.tool_calls
        # IF: The LLM wants to call tools
        if tool_calls:
            messages.append(response_msg) # Add the "intent" to history
            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                
                print(f"🛠️ Agent calling: {fn_name} with {fn_args}")

                # Execute the function
                function_to_call = AVAILABLE_FUNCTIONS.get(fn_name)
                if function_to_call:
                    tool_result = function_to_call(**fn_args)
                else:
                    tool_result = f"Error: Function {fn_name} not found."

                # Add the result to history
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": fn_name,
                    "content": str(tool_result)
                })
                
            # The loop continues... sending the tool result back to OpenAI 
            # so it can decide what to do next (e.g., call another tool or finish).
        
        # ELSE: The LLM has a final answer (no more tools needed)
        else:
            return response_msg.content