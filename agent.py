"""
LangChain Agent Setup with Tools
"""
import os
import json
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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
      
        
        # Get API key from multiple sources (priority order):
        # 1. Environment variable (OPENAI_API_KEY)
        # 2. .env file (via load_dotenv)
        # 3. config.json file
        # 4. Fallback to hardcoded key
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Fallback 1: Try loading from .env again
        if not api_key:
            load_dotenv(override=True)
            api_key = os.getenv("OPENAI_API_KEY")
        
        # Fallback 2: Try loading from config.json
        if not api_key:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        api_key = config.get("openai_api_key")
                except Exception:
                    pass
        
        # Final check - ensure we have a valid API key
        if not api_key or api_key.strip() == "":
            raise ValueError("OPENAI_API_KEY not found in environment variables, .env file, config.json, or fallback")
        
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
