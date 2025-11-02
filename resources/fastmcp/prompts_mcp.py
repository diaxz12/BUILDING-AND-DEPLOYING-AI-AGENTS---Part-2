from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent

mcp = FastMCP(name="PromptServer")

# Basic prompt returning a string (converted to user message automatically)
@mcp.prompt
def ask_about_topic(topic: str) -> str:
    """Generates a user message asking for an explanation of a topic."""
    return f"Can you please explain the concept of '{topic}'?"

# Prompt returning a specific message type
@mcp.prompt
def generate_code_request(language: str, task_description: str) -> PromptMessage:
    """Generates a user message requesting code generation."""
    content = f"Write a {language} function that performs the following task: {task_description}"
    return PromptMessage(role="user", content=TextContent(type="text", text=content))

if __name__ == "__main__":
    mcp.run()