# FastAPI + LangChain Agent Project

A basic tool-using agent project that combines FastAPI for the API layer and LangChain for agent orchestration with OpenAI.

## Features

- **FastAPI REST API** for interacting with the agent
- **LangChain Agent** with tool-using capabilities
- **OpenAI Integration** using GPT-3.5-turbo
- **Example Tools**:
  - Calculator: Performs basic arithmetic operations
  - Time: Gets current date and time
  - Echo: Simple echo tool for testing

## Project Structure

```
my_first_project/
├── main.py              # FastAPI app and endpoints
├── agent.py             # LangChain agent setup
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Setup Instructions

virtual env install 

```bash
python3 -m venv .venv
```


### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   APP_API_KEY=your_app_api_key_here
   ```

### 3. Run the Application

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check (public)
- **GET** `/` or `/health` - Check if the API is running

### Protected Endpoints (require `X-API-Key` header)
- **POST** `/chat` - Interact with the agent
- **/items** CRUD routes
- **/categories** CRUD routes

Example protected header:
```http
X-API-Key: your_app_api_key_here
```

**Request Body:**
```json
{
  "message": "What is 25 * 4?",
  "chat_history": []  // Optional
}
```

**Response:**
```json
{
  "response": "The result of 25 * 4 is 100.",
  "tools_used": ["calculator"],
  "success": true
}
```

## Example Usage

### Using curl

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "X-API-Key: your_app_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 25 * 4?"}'
```

### Using Python requests

```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "What is 25 * 4?"}
)
print(response.json())
```

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Available Tools

1. **Calculator**: Performs arithmetic calculations
   - Example: "Calculate 10 + 5 * 2"

2. **Get Current Time**: Returns current date and time
   - Example: "What time is it?"

3. **Echo**: Echoes back the input (for testing)
   - Example: "Echo: Hello World"

## Error Handling

The API includes proper error handling for:
- Missing or invalid API keys
- Empty messages
- Agent execution errors
- Configuration issues

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Notes

- Make sure you have a valid OpenAI API key
- The agent uses GPT-3.5-turbo by default (can be changed in `agent.py`)
- CORS is enabled for all origins (adjust in production)
- The agent maintains conversation history if provided

## License

This is a basic example project for educational purposes.
