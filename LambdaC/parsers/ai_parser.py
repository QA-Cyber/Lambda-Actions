# parsers/ai_parser.py
import logging
from internal_model import LambdaPlaybook
from ai_transformer import openai_client, clean_ai_response
from tenacity import retry, wait_fixed, stop_after_attempt
import ruamel.yaml
logger = logging.getLogger(__name__)

# Your official Lambda-Actions schema (v1.2) as a JSON/YAML snippet:
LAMBDA_SCHEMA_DOC = """
### Lambda-Actions YAML Schema

# Top-level metadata for Lambda-Action playbook identification and management
id: STRING                        
name: STRING                      
description: STRING

# Trigger definition
trigger:
  type: ENUM(manual | scheduled | event)
  schedule: STRING                 # Cron expression (if type = scheduled)
  event:
    source: STRING                 # Generic event source identifier
    on: ENUM(create | update)      # Indicates when the trigger fires
    fields: [STRING]               # Optional list of fields (used if on: update)
    filters: MAP                   # Key-value filters for triggering logic

# Steps definition
steps:
  - id: STRING                      # Unique step identifier
    type: ENUM(action | condition | subplaybook | manual | script | task)
    description: STRING             # Optional detailed description

    # ACTION step: executes an abstract action
    action: STRING                  # Action/command identifier
    connector: STRING (optional)    # Connector/integration name
    inputs: MAP                     # Input parameters for the action
    outputs: MAP                    # Output variables to store results

    # CONDITION step: branching logic
    conditions:
      - if: STRING                  # Expression to evaluate
        then: STRING                # Step ID to continue if true
        else: STRING                # Step ID if false

    # SUBPLAYBOOK step: reusable nested logic
    subplaybooks: [STRING]          # List of subplaybook identifiers
    parallel: BOOLEAN               # Whether to run subplaybooks in parallel
    inputs: MAP                     # Inputs passed to subplaybooks
    outputs: MAP                    # Outputs returned from subplaybooks

    # MANUAL step: human input or approval
    instructions: STRING            # Analyst instructions
    timeout: INTEGER                # Timeout in minutes
    escalation:
      notify: [STRING]              # Who to notify
      escalate_after: INTEGER       # When to escalate (in minutes)

    # SCRIPT step: custom logic block
    runtime: ENUM(python | javascript | lua)
    script_content: STRING          # The actual script code
    inputs: MAP                     # Script input parameters
    outputs: MAP                    # Script output variables

    # TASK step: arbitrary logic block
    task_definition:
      type: STRING                  # Task type
      parameters: MAP               # Task parameters
      description: STRING           # Description of task purpose
      outputs: MAP                  # Resulting output variables

# Inputs to the playbook
inputs:
  - name: STRING
    description: STRING
    default: ANY

# Outputs from the playbook
outputs:
  - name: STRING
    description: STRING
    value: ANY
"""

@retry(wait=wait_fixed(3), stop=stop_after_attempt(2))
def parse_with_ai(filepath: str) -> LambdaPlaybook:
    """
    Use AI to convert any SOAR playbook (YAML or JSON) into the Lambda-Actions format.
    The AI must emit pure YAML matching the official Lambda-Actions schema above.
    """
    try:
        raw_text = open(filepath, 'r').read()
    except OSError as e:
        raise RuntimeError(f"Cannot read playbook file: {e}")

    system = {
        "role": "system",
        "content": (
            "You are an expert SOAR playbook transformer.\n"
            "Emit ONLY valid YAML that conforms exactly to the Lambda-Actions schema below:\n\n"
            + LAMBDA_SCHEMA_DOC
        )
    }
    user = {
        "role": "user",
        "content": f"```yaml\n{raw_text}\n```"
    }

    resp = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[system, user],
        temperature=0,
        max_tokens=16000,
    )
    ai_output = resp.choices[0].message.content
    cleaned = clean_ai_response(ai_output)

    # Parse the YAML AI returned
    yaml = ruamel.yaml.YAML(typ='safe')
    try:
        data = yaml.load(cleaned)
    except Exception as e:
        raise ValueError(f"AI output is not valid YAML: {e}\nOutput was:\n{cleaned}")

    # Validate with Pydantic model
    try:
        lambda_pb = LambdaPlaybook.model_validate(data)
    except Exception as e:
        raise ValueError(f"Failed to coerce AI output into LambdaPlaybook: {e}\nParsed data:\n{data}")

    return lambda_pb
