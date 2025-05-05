# internal_model.py
from typing import List, Optional, Dict
from pydantic import BaseModel

class ConditionBranch(BaseModel):
    option: str
    next_step: str
    condition: Optional[str] = None

class Step(BaseModel):
    id: str
    name: str
    type: str  # 'action', 'condition', 'manual', 'start', etc.
    description: Optional[str] = None
    action: Optional[str] = None
    conditions: Optional[List[ConditionBranch]] = None
    next_steps: Optional[List[str]] = None
    inputs: Optional[Dict] = None
    outputs: Optional[Dict] = None
    metadata: Optional[Dict] = None

class LambdaPlaybook(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    steps: List[Step]
    metadata: Optional[Dict] = None
