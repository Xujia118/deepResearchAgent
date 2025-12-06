from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class DeepResearchAgent:
    """
    The Agent holds the identity, model configuration, and tools.
    It is responsible for generating the raw response from the LLM.
    """
    def __init__(self, model, tools=None, instructions=""):
        self.client = OpenAI()
        self.model = model
        self.instructions = instructions

    def generate_response(self, input_list, tools=None, override_instructions=None):
        """
        Single atomic interaction with the LLM.
        The Agent doesn't know *how* to execute tools, only that they exist.
        """
        active_instructions = override_instructions or self.instructions

        response = self.client.responses.create(
            model=self.model,
            tools=tools,
            instructions=active_instructions,
            input=input_list
        )
        return response

