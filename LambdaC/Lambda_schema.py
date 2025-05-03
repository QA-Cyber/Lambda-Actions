# lambda_schema.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Trigger(BaseModel):
    type: str                   # manual | scheduled | event
    schedule: Optional[str]     # cron expression if scheduled
    event: Optional[Dict[str, Any]]

class ConditionBranch(BaseModel):
    if_: str                    # renamed because `if` is reserved
    then: str
    else_: Optional[str]

class StepSchema(BaseModel):
    id: str
    type: str                   # action | condition | subplaybook | …
    description: Optional[str]
    action: Optional[str]
    connector: Optional[str]
    inputs: Optional[Dict[str, Any]]
    outputs: Optional[Dict[str, Any]]
    conditions: Optional[List[ConditionBranch]]
    subplaybooks: Optional[List[str]]
    parallel: Optional[bool]
    instructions: Optional[str]
    timeout: Optional[int]
    escalation: Optional[Dict[str, Any]]
    runtime: Optional[str]      # python | javascript | lua
    script_content: Optional[str]
    task_definition: Optional[Dict[str, Any]]

class LambdaSchema(BaseModel):
    id: str
    name: str
    description: Optional[str]
    trigger: Optional[Trigger]
    steps: List[StepSchema]
    inputs: Optional[List[Dict[str, Any]]]
    outputs: Optional[List[Dict[str, Any]]]
    metadata: Optional[Dict[str, Any]]
