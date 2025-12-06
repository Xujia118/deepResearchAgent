from agent import DeepResearchAgent
from registry import ToolRegistry
from controller import Controller
from register_tools import register as register_tools
from formatter import format_print


if __name__ == "__main__":
    agent = DeepResearchAgent("gpt-5-nano")
    
    registry = ToolRegistry()
    register_tools(registry)
    
    agent_controller = Controller(agent, registry)

    input_list = [
        {
            "role": "user", 
            "content": "Find the latest release notes for the Python 'MCP' (Model Context Protocol) SDK. What is the specific version number, and what is one key feature listed in that version?"
        }]
    
    response = agent_controller.run(input_list)

    format_print(input_list)
    print("\nFinal Output:")
    print(response.output_text)

