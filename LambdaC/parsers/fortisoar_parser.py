# fortisoar_parser.py
import json
from internal_model import LambdaPlaybook, Step, ConditionBranch


def identify_step_type(step_data: dict, incoming_routes: set) -> str:
    args = step_data.get("arguments", {})
    name = (step_data.get("name") or "").strip().lower()

    if "response_mapping" in args:
        return "manual"

    if args.get("conditions") or args.get("response_mapping", {}).get("options"):
        return "condition"

    uid = step_data.get("uuid")
    if "start" in name or uid not in incoming_routes:
        return "start"

    if not args.get("operation") and not args.get("scriptName") and not args.get("response_mapping"):
        return "title"

    return "action"


def parse_fortisoar(filepath: str) -> LambdaPlaybook:
    with open(filepath) as f:
        data = json.load(f)

    incoming = {r.get("targetStep", "").split("/")[-1] for r in data.get("routes", [])}

    steps = []
    for idx, s in enumerate(data.get('steps', [])):
        step_id = s.get("uuid", f"step-{idx}")

        conditions = None
        args = s.get("arguments", {})
        if "response_mapping" in args:
            options = args["response_mapping"].get("options", [])
            conditions = [
                ConditionBranch(
                    option=o.get("option", "#default#"),
                    next_step=o.get("step_iri", "").split("/")[-1],
                    condition=o.get("condition")
                ) for o in options
            ]

        step = Step(
            id=step_id,
            name=s.get("name", f"Unnamed Step"),
            type=identify_step_type(s, incoming),
            description=s.get("description"),
            action=args.get("operation") or None,
            inputs=args,
            outputs=None,
            conditions=conditions,
            metadata={
                "raw_arguments": args,
                "stepType": s.get("stepType")
            }
        )
        steps.append(step)

    uuid_to_nextsteps = {}
    for r in data.get("routes", []):
        source = r.get("sourceStep", "").split("/")[-1]
        target = r.get("targetStep", "").split("/")[-1]
        uuid_to_nextsteps.setdefault(source, []).append(target)

    for step in steps:
        if step.id in uuid_to_nextsteps:
            step.next_steps = uuid_to_nextsteps[step.id]

    return LambdaPlaybook(
        id=data.get("uuid", "unknown-playbook"),
        name=data.get("name", "Unnamed Playbook"),
        description=data.get("description"),
        steps=steps
    )