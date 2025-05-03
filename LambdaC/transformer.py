# transformers.py
from Lambda_schema import LambdaSchema, StepSchema, ConditionBranch
from internal_model import LambdaPlaybook

def to_general_lambda(pb: LambdaPlaybook) -> LambdaSchema:
    steps = []
    for s in pb.steps:
        conds = None
        if s.conditions:
            conds = [
                ConditionBranch(if_=c.condition or "",
                                then=c.next_step,
                                else_=None)
                for c in s.conditions
            ]
        steps.append(
            StepSchema(
                id=s.id,
                type=s.type,
                description=s.description,
                action=s.action,
                connector=(s.metadata or {}).get("connector"),
                inputs=s.inputs,
                outputs=s.outputs,
                conditions=conds,
                subplaybooks=None,
                parallel=None,
                instructions=None,
                timeout=None,
                escalation=None,
                runtime=None,
                script_content=None,
                task_definition=None,
            )
        )
    return LambdaSchema(
        id=pb.id,
        name=pb.name,
        description=pb.description,
        trigger=None,
        steps=steps,
        inputs=None,
        outputs=None,
        metadata={"vendor_mappings": {}},
    )
