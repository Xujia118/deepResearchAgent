import json
from agent import DeepResearchAgent
from registry import ToolRegistry


class Controller:
    def __init__(self, agent: DeepResearchAgent, registry: ToolRegistry):
        self.agent = agent
        self.registry = registry

    def run(self, input_list, max_attempts=5, stop_keyword=None):
        attempts = 0

        # Get the "Menu" of tools once
        tool_defs = self.registry.get_all_tools()

        while attempts < max_attempts:
            # --- 1. Agent Decides ---
            # We pass the tool_defs here explicitly. The Agent doesn't store them.
            response = self.agent.generate_response(
                input_list,
                tools=tool_defs,
                override_instructions="Decide the next step. If you have the answer, output it directly."
            )

            # Update history with the Agent's decision
            input_list += response.output

            # --- 2. Controller Executes Tools ---
            tools_called = False

            for item in response.output:
                if item.type == "function_call":
                    tools_called = True
                    self._execute_tool(input_list, item)

            # --- 3. Check for Termination ---
            # If no tools were called, the Agent likely gave a text answer.
            if not tools_called:
                break

            # Optional: Check for specific keyword in history
            if stop_keyword and self._contains_keyword(input_list, stop_keyword):
                break

            attempts += 1

        # Final Summary Step
        final_resp = self.agent.generate_response(
            input_list,
            override_instructions="Summarize the final findings clearly."
        )
        return final_resp

    def _execute_tool(self, input_list, item):
        """Finds the tool in Registry, runs it, and saves output."""
        func = self.registry.get_function(item.name)

        if func:
            try:
                args = json.loads(item.arguments)
                result = func(**args)
            except Exception as e:
                result = f"Error executing {item.name}: {str(e)}"
        else:
            result = f"Error: Tool {item.name} not found."

        # Append result to history in the format the API expects
        input_list.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps({item.name: result})
        })

    def _contains_keyword(self, input_list, keyword):
        # Scan the last few items for the keyword
        for item in reversed(input_list):
            # output content is often in item.content or function outputs
            if hasattr(item, "content") and item.content and keyword in item.content:
                return True
        return False
