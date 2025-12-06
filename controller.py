import json
import re
from agent import DeepResearchAgent
from registry import ToolRegistry


class Controller:
    def __init__(self, agent, registry, planner):
        self.agent = agent
        self.registry = registry
        self.planner = planner 

    def run(self, history):
        """
        Executes the planning loop. 
        'history' is injected from main (the input_list).
        """
        # 1. Bootstrap: Ensure the user's initial prompt is in the planner
        # We look at the last user message to start the task list
        last_message = next((m for m in reversed(history)
                            if m["role"] == "user"), None)
        if last_message and self.planner.is_empty():
            self.planner.add_task(last_message["content"], priority=1)

        step_count = 0
        max_steps = 10

        while not self.planner.is_empty() and step_count < max_steps:
            # 2. Get next task
            current_task = self.planner.get_next_task()
            print(
                f"\n--- Step {step_count + 1} | Executing: {current_task.question} ---")

            # 3. Add context to history so Agent knows what it is doing
            # We append to the injected 'history' list directly
            history.append(
                {"role": "user", "content": f"Current Priority Task: {current_task.question}"})

            # 4. Agent Thinks
            tool_defs = self.registry.get_all_tools()
            response = self.agent.generate_response(
                history,
                tool_defs,
                override_instructions="You are a researcher. Use tools to answer the current task. If you find a URL, read it."
            )

            # 5. Execute Tools & Update History
            tool_outputs = []

            # Helper to append response items to history
            if response.output:
                for item in response.output:
                    # Append raw item (message or tool call)
                    history.append(item)

                    if item.type == "function_call":
                        result, tool_name = self._execute_tool(item)
                        tool_outputs.append((tool_name, result))

                        # Append result
                        history.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps({tool_name: result})
                        })

            # 6. Re-planning (Gap Detector)
            for tool_name, result in tool_outputs:
                self._gap_detector(tool_name, result)

            step_count += 1

        # Final Summary
        print("\n--- Work Complete. Generating Summary ---")
        final_resp = self.agent.generate_response(
            history,
            override_instructions="Review the findings and provide a final comprehensive answer."
        )
        return final_resp

    def _execute_tool(self, item):
        func = self.registry.get_function(item.name)
        if func:
            try:
                args = json.loads(item.arguments)
                result = func(**args)
            except Exception as e:
                result = f"Error: {e}"
        else:
            result = "Error: Tool not found"
        return result, item.name

    def _gap_detector(self, tool_name, result):
        """Analyzes results to inject new tasks into the planner."""
        if tool_name == "web_search":
            # Simple heuristic: Look for URLs in search results
            urls = re.findall(
                r'https?://[^\s<>"]+|www\.[^\s<>"]+', str(result))
            if urls:
                # Drill down on the first promising link
                target = urls[0]
                self.planner.add_task(
                    f"Read content from: {target}", priority=0)

        elif tool_name == "read_url" or tool_name == "extract_text":
            # If text is too short or mentions "see more", we might search again
            if len(result) < 200 and "moved" in result.lower():
                self.planner.add_task(
                    f"Search for the new location of this content", priority=1)
