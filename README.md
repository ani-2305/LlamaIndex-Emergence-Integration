# LlamaIndex + Emergence Integration

This repository demonstrates how to integrate [LlamaIndex](https://github.com/jerryjliu/gpt_index) with [Emergence AI's Web Orchestrator](https://api.emergence.ai/). It uses **OpenAI** for language model capabilities, and **Emergence AI** for web automation workflows.

---

## Project Overview

- **`llamaindex-integration.py`**: Main Python file that:
  1. Loads your API keys from a `.env` file.
  2. Defines a function to create and poll an Emergence AI web workflow.
  3. Wraps that function as a **tool** for LlamaIndex.
  4. Uses an **OpenAIAgent** from LlamaIndex to handle user queries and call the Emergence tool when needed.

- **`.env`**: File containing secret keys, like `OPENAI_API_KEY` and `EMERGENCE_API_KEY`. (This file is gitignored so your keys remain private.)

- **`requirements.txt`**: Python dependencies.

---

## Setup Instructions

### 1. Clone the Repository

If you haven’t already:

```
git clone https://github.com/ani-2305/LlamaIndex-Emergence-Integration.git
cd LlamaIndex-Emergence-Integration
```

*(If you’re reading this after pulling changes, just `cd` into the local folder.)*

### 2. Create a Python Virtual Environment (Optional)

```bash
python3 -m venv venv
source venv/bin/activate
```

*(On Windows PowerShell: `.\venv\Scripts\activate`.)*

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- [LlamaIndex](https://github.com/jerryjliu/gpt_index)  
- [OpenAI Python library](https://pypi.org/project/openai/)  
- [Requests](https://pypi.org/project/requests/)  
- [python-dotenv](https://pypi.org/project/python-dotenv/)  

### 4. Add Your `.env` File

Create a file named `.env` in the same directory:

```
OPENAI_API_KEY="<your-openai-key>"
EMERGENCE_API_KEY="<your-emergence-key>"
```

These environment variables are used by:
- `llama_index.llms.openai.OpenAI` for LLM calls,
- and the Emergence function for web orchestrator API calls.

*(Ensure `.env` is in your `.gitignore` so you don’t commit secrets.)*

### 5. Run the Script

```bash
python llamaindex-integration.py
```

When prompted, enter a **web automation prompt**—for instance:
```
Please go to CNN.com and find the latest AI investment news.
```

- The LlamaIndex agent uses your **OpenAI** model to parse the request.  
- It calls the Emergence “web orchestrator” tool if it decides it needs web automation.  
- The script prints the final answer to your console.

### 6. Verify or Debug

- If you see `No EMERGENCE_API_KEY found...`, ensure `.env` has the correct key name and value.  
- If you see “Error creating Emergence workflow,” check your Emergence AI subscription or network status.  
- If the agent never calls Emergence, you can guide it in the conversation (e.g. “Use the web orchestrator tool to accomplish this.”).

---

## File-by-File Summary

- **`emergence_llamaindex.py`**  
  Main entry point. Shows how to:
  1. Load environment variables with `python-dotenv`.
  2. Initialize the Emergence web orchestrator function.
  3. Create a LlamaIndex `OpenAIAgent` with a custom tool.

- **`.env`**  
  Contains your `OPENAI_API_KEY` and `EMERGENCE_API_KEY`. **Not** committed to source control if `.gitignore` is set up.

- **`requirements.txt`**  
  Defines the Python libraries needed for the project.

- **`README.md`**  
  (This document!) Explains how to set up and run the integration.

---
