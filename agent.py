"""
LangChain Agent Setup with Tools
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

# Load .env from the project directory (same folder as this file), not only the process cwd
_DOTENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_DOTENV_PATH)


@tool
def calculator(expression: str) -> str:
    """
    Performs basic arithmetic calculations.
    
    Args:
        expression: A mathematical expression as a string (e.g., "25 * 4", "10 + 5", "100 / 2")
    
    Returns:
        The result of the calculation as a string
    """
    try:
        # Safely evaluate the expression
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def get_current_time() -> str:
    """
    Gets the current date and time.
    
    Returns:
        Current date and time as a string
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def echo(message: str) -> str:
    """
    Echoes back the input message. Useful for testing.
    
    Args:
        message: The message to echo back
    
    Returns:
        The same message
    """
    return message


class AgentService:
    """Service class for managing the LangChain agent"""
    
    def __init__(self):
        """Initialize the agent with OpenAI model and tools"""
        # Load .env but do NOT override existing env vars — terminal export wins.
        # load_dotenv(_DOTENV_PATH, override=False)

        # Priority order:
        # 1. .env (loaded above with override=True into OPENAI_API_KEY)
        # 2. Existing environment variable OPENAI_API_KEY
        # 3. config.json file
        api_key = os.getenv("OPENAI_API_KEY")

        # Fallback: Try loading from config.json
        if not api_key:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                        api_key = config.get("openai_api_key")
                except Exception:
                    pass

        # Final check - ensure we have a valid API key
        if not api_key or api_key.strip() == "":
            raise ValueError("OPENAI_API_KEY not found in .env, environment variables, or config.json")

        # Initialize the LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,  
            api_key=api_key
        )
        
        # Define available tools
        self.tools = [calculator, get_current_time, echo]
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that can use tools to answer questions. "
                      "When you need to perform calculations, get the current time, or test something, "
                      "use the available tools. Always be concise and helpful."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def process_message(self, message: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process a user message through the agent.
        
        Args:
            message: The user's message
            chat_history: Optional list of previous messages in format [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Convert chat history to LangChain message format
            langchain_messages = []
            if chat_history:
                for msg in chat_history:
                    if msg.get("role") == "user":
                        langchain_messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        langchain_messages.append(AIMessage(content=msg.get("content", "")))
            
            # Run the agent
            result = self.agent_executor.invoke({
                "input": message,
                "chat_history": langchain_messages
            })
            
            # Extract tools used from the execution trace
            tools_used = []
            if isinstance(result, dict) and 'intermediate_steps' in result:
                for step in result.get('intermediate_steps', []):
                    if step and len(step) > 0:
                        # Extract tool name from the action
                        action = step[0]
                        if hasattr(action, 'tool'):
                            tools_used.append(action.tool)
                        elif hasattr(action, 'tool_name'):
                            tools_used.append(action.tool_name)
                        elif isinstance(action, str):
                            tools_used.append(action)
                        else:
                            tools_used.append(str(type(action).__name__))
            
            return {
                "response": result.get("output", "No response generated"),
                "tools_used": tools_used,
                "success": True
            }
        except Exception as e:
            return {
                "response": f"Error processing message: {str(e)}",
                "tools_used": [],
                "success": False
            }


# Global agent instance
_agent_service = None


def reset_agent_service():
    """Reset the cached agent service (useful for reinitialization)"""
    global _agent_service
    _agent_service = None


def get_agent_service() -> AgentService:
    """Get or create the global agent service instance"""
    global _agent_service
    try:
        if _agent_service is None:
            _agent_service = AgentService()
        return _agent_service
    except Exception as e:
        # Reset to None so it can retry on next call
        _agent_service = None
        # Re-raise the exception with a clearer message
        error_msg = str(e)
        if "OPENAI_API_KEY" in error_msg:
            raise ValueError(f"OPENAI_API_KEY not found: {error_msg}")
        raise e
