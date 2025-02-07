import os
import time
import requests
import uuid

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

BASE_URL = "https://api.emergence.ai/v0/orchestrators/em-orchestrator/workflows"

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
        "Client-ID": str(uuid.uuid4())
    }

    # Step A: Create the workflow
    try:
        create_resp = requests.post(BASE_URL, headers=headers, json={"prompt": prompt})
        create_resp.raise_for_status()

        # Print the workflow ID
        workflow_id = create_resp.json()["workflowId"]
        print(f"Workflow ID: {workflow_id}")
    except Exception as e:
        return f"Error creating Emergence workflow: {e}"

    # Step B: Poll until success/fail
    poll_url = f"{BASE_URL}/{workflow_id}"

    poll_count = 1
    while True:
        print(f"\nPolling attempt {poll_count}...")
        poll_count += 1

        try:
            poll_resp = requests.get(poll_url, headers=headers)
            poll_resp.raise_for_status()

            # Look inside "data" for "status" and "output"
            response_json = poll_resp.json()
            data_obj = response_json.get("data", {})
            status = data_obj.get("status", "UNKNOWN")

            if status == "SUCCESS":
                # Return the final textual result from the "output" key
                return data_obj.get("output", "No output provided by Emergence.")
            elif status in ("FAILED", "TIMEOUT"):
                return f"Workflow ended with status {status}"

        except Exception as e:
            error_details = {
                "error": str(e),
                "response_text": poll_resp.text if poll_resp else None,
                "status_code": poll_resp.status_code if poll_resp else None
            }
            return f"Polling error: {error_details}"

        # Wait 15 seconds between polls
        time.sleep(15)

##############################################################################
# 4) Wrap the Emergence Function as a LlamaIndex Tool
##############################################################################
emergence_tool = FunctionTool.from_defaults(fn=emergence_web_orchestrator)

##############################################################################
# 5) Create LLM and Agent
##############################################################################
# LlamaIndex's OpenAI wrapper automatically uses OPENAI_API_KEY from the env.
# If you want to pass it explicitly, do: OpenAI(openai_api_key=OPENAI_API_KEY, ...)
llm = OpenAI(model="gpt-4o", temperature=0)

agent = OpenAIAgent.from_tools(
    tools=[emergence_tool],
    llm=llm,
    verbose=False,  # hides debug info about function calling
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
    user_query = input("\nEnter a web automation prompt: ")

    # Let the agent handle the query
    response = agent.chat(user_query)
    print("\n=== Agent Response ===")
    print(response)

if __name__ == "__main__":
    main()
