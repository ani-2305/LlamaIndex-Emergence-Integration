import os
import time
import requests

# 1) Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool
from llama_index.agent.openai import OpenAIAgent

##############################################################################
# 2) Read Keys from Environment
##############################################################################
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMERGENCE_API_KEY = os.getenv("EMERGENCE_API_KEY")

BASE_URL = "https://api.emergence.ai/v0/orchestrators/em-web-automation/workflows"

##############################################################################
# 3) Define Emergence Web Orchestrator Function
##############################################################################
def emergence_web_orchestrator(prompt: str) -> str:
    """
    Create and poll Emergence AI's web orchestrator workflow with the given prompt.
    Returns the final text result upon success, or a status message if failed/timed out.
    """
    if not EMERGENCE_API_KEY:
        return "No EMERGENCE_API_KEY found in environment variables."

    headers = {
        "apikey": EMERGENCE_API_KEY,
        "Content-Type": "application/json",
    }

    # Step A: Create the workflow
    try:
        create_resp = requests.post(BASE_URL, headers=headers, json={"prompt": prompt})
        create_resp.raise_for_status()
        workflow_id = create_resp.json()["workflowId"]
    except Exception as e:
        return f"Error creating Emergence workflow: {e}"

    # Step B: Poll until success/fail
    poll_url = f"{BASE_URL}/{workflow_id}"
    while True:
        try:
            poll_resp = requests.get(poll_url, headers={"apikey": EMERGENCE_API_KEY})
            poll_resp.raise_for_status()

            data = poll_resp.json()["data"]
            status = data["status"]

            if status == "SUCCESS":
                # Return final textual result
                return data["output"]["result"]
            elif status in ("FAILED", "TIMEOUT"):
                return f"Workflow ended with status {status}"

        except Exception as e:
            return f"Error polling Emergence workflow: {e}"

        # Wait 5 seconds between polls
        time.sleep(5)

##############################################################################
# 4) Wrap the Emergence Function as a LlamaIndex Tool
##############################################################################
emergence_tool = FunctionTool.from_defaults(fn=emergence_web_orchestrator)

##############################################################################
# 5) Create LLM and Agent
##############################################################################
# LlamaIndex's OpenAI wrapper automatically uses OPENAI_API_KEY from the env
# If you want to pass it explicitly, do: OpenAI(openai_api_key=OPENAI_API_KEY, ...)
llm = OpenAI(model="gpt-4o", temperature=0)

agent = OpenAIAgent.from_tools(
    tools=[emergence_tool],
    llm=llm,
    verbose=True,  # shows debug info about function calling
    system_prompt=(
        "You are a helpful agent with the 'emergence_web_orchestrator' tool. "
        "Use it whenever the user wants to perform web automation tasks. "
        "Return final answers plainly."
    ),
)

##############################################################################
# 6) Main: Prompt user, run the agent
##############################################################################
def main():
    # Make sure we have an OpenAI key
    if not OPENAI_API_KEY:
        print("No OPENAI_API_KEY found in environment variables.")
        return

    print("Welcome to Emergence + LlamaIndex agent!")
    user_query = input("Enter a web automation prompt: ")

    # Let the agent handle the query
    response = agent.chat(user_query)
    print("\n=== Agent Response ===")
    print(response)

if __name__ == "__main__":
    main()
