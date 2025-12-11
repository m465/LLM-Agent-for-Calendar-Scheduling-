# LLM Agent for Calendar Scheduling

This project implements an AI-powered calendar agent capable of checking schedules, finding meeting times, and blocking time slots using natural language queries. It uses OpenAI's GPT models effectively to function as an intelligent assistant.

## Features

- **Natural Language Understanding**: Chat with the agent to manage your calendar.
- **Tools**:
  - `check_schedule`: View events for a specific date.
  - `get_next_meeting_with`: Find upcoming meetings with specific people.
  - `block_time_slot`: Schedule new events while checking for conflicts.
- **API**: Exposed via FastAPI for easy integration.

## Prerequisites

- Python 3.8+
- OpenAI API Key

## Setup

1.  **Clone the repository** (if you haven't already).

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**:
    Create a `.env` file in the root directory and add your OpenAI API key:
    ```env
    OPENAI_API_KEY=your_api_key_here
    ```

## Usage

1.  **Start the Server**:
    Run the `main.py` file:
    ```bash
    python main.py
    ```
    The server will start at `http://localhost:8000`.

2.  **Interact with the Agent**:
    - **API Docs**: Visit `http://localhost:8000/docs` to test the endpoints interactively.
    - **Chat Endpoint**: Send POST requests to `/chat` with a JSON body:
      ```json
      {
        "query": "What do I have planned for today?"
      }
      ```

## Project Structure

- `main.py`: FastAPI application entry point.
- `agent.py`: Core logic for the LLM agent, handling tool calling and conversation flow.
- `tools.py`: Implementation of calendar tools (check schedule, block time, etc.) and file operations.
- `calendar.json`: Local JSON-based database for storing calendar events.
