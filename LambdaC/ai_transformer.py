# ai_transformer.py
import hashlib
import json
import os
import openai
from dotenv import load_dotenv
from internal_model import LambdaPlaybook
from tenacity import retry, wait_fixed, stop_after_attempt

load_dotenv()
# Initialize OpenAI client (v1.x API)
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MCP_CONTEXT = """
You are an expert in converting Lambda-Actions schema playbooks into Cortex XSOAR playbook JSON.
Below are four real-world XSOAR playbook patterns to learn from:
  • **Default** (generic incident lifecycle with extract, dedupe, analysis, containment, reporting)  
  • **SOCRadar Incident** (integrations, manual review form, false-positive vs true-positive branching)  
  • **JOB – Cortex XDR query endpoint device control violations** (scheduled run, grid creation, new incident)  
  • **Cortex XDR – Block File** (integration-enabled check, yes/no branches, block list command)  

**Key mapping rules**  
- **Step types** → XSOAR:  
  – Start → `start`  
  – WorkflowStep → `regular`  
  – Condition (or tasks with `conditions`/`response_mapping`) → `condition`  
  – Manual Task / Collection → `collection` or `condition` (preserving forms/messages)  
  – Title → `title`  
  – Nested calls to other playbooks → `playbook` (use `playbookName`)  
- **Fields to preserve**:  
  – `script` or `scriptName` → `scriptName`  
  – `scriptarguments` / `playbookName`  
  – `conditions` array (with `label`, `operator`, `left`, `right`)  
  – `loop`, `timertriggers`  
  – UI/layout fields: `view`, `note`, `ignoreworker`  
  – execution flags: `continueonerror`, `skipunavailable`, `quietmode`, `isoversize`, `isautoswitchedtoquietmode`  
- **Branching**:  
  – Use `"nexttasks"` with either a `"#none#"` array for linear flows or keys matching each branch label.  
- **Task structure**:  
  – Output a `"tasks"` object keyed by `"0"`, `"1"`, …  
  – Each task must have:
    ```json
    {
      "id": "<string index>",
      "taskid": "<original UUID>",
      "type": "<regular|condition|start|title|playbook|collection>",
      "task": {
         "id": "<UUID>",
         "version": -1,
         "name": "<step name>",
         "description": "<desc|null>",
         "scriptName": "<cmd|null>",
         "type": "<same as task.type>",
         "iscommand": <true|false>,
         "brand": "<integration|null>",
         // and if playbook, include "playbookName"
      },
      "nexttasks": { ... },
      // plus any of the preserved flags/fields
    }
    ```
- **Top-level**:  
  ```json
  {
    "id": "<playbook UUID>",
    "name": "<playbook name>",
    "version": -1,
    "description": "<desc|null>",
    "starttaskid": "<index of Start>",
    "tasks": { ... }
  }
Do NOT invent new fields or omit anything present in the Lambda input. """





def clean_ai_response(text: str) -> str:
    """Remove Markdown fences or language hints"""
    # strip code fences
    if text.startswith('```'):
        parts = text.split('```')
        if len(parts) >= 3:
            text = parts[1]
    return text.strip()

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_key(data: dict) -> str:
    payload = json.dumps(data, sort_keys=True).encode()
    return hashlib.md5(payload).hexdigest()


def cached_transform(lambda_playbook: dict, vendor: str = "general") -> dict:
    key = _cache_key(lambda_playbook)
    vendor_dir = os.path.join(CACHE_DIR, vendor)
    os.makedirs(vendor_dir, exist_ok=True)
    cache_file = os.path.join(vendor_dir, f"{key}.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    result = ai_transform(lambda_playbook)
    with open(cache_file, 'w') as f:
        json.dump(result, f, indent=2)
    return result


@retry(wait=wait_fixed(5), stop=stop_after_attempt(3))
def ai_transform(lambda_playbook: dict) -> dict:
    prompt = f"{MCP_CONTEXT}\n\nLambda Playbook JSON:\n{json.dumps(lambda_playbook, indent=2)}"
    system = {"role": "system", "content": "You are a JSON-only transformer. Output only valid JSON (no markdown or extra text)."}
    user   = {"role": "user",   "content": f"{MCP_CONTEXT}\n\nLambda Playbook JSON:\n{json.dumps(lambda_playbook, indent=2)}"}
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[system, user],
         temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()
    # snip off anything before the first { and after the last }
    start = raw.find('{')
    end   = raw.rfind('}')
    if start == -1 or end == -1:
        print("❌ No JSON braces found in AI response:", raw)
        raise ValueError("Invalid JSON from AI")
    body = raw[start:end+1]
    return json.loads(body)
