# xsoar_parser.py
import ruamel.yaml
from internal_model import LambdaPlaybook, Step, ConditionBranch

def infer_xsoar_step_type(t: dict) -> str:
    if t.get("type") == "start":
        return "start"
    elif t.get("type") == "condition":
        return "condition"
    elif t.get("type") == "title":
        return "title"
    elif t.get("type") == "playbook":
        return "subplaybook"
    else:
        return "action"

def parse_xsoar_yaml(path: str) -> LambdaPlaybook:
    yaml = ruamel.yaml.YAML()
    with open(path, 'r') as f:
        data = yaml.load(f)

    steps = []
    tasks = data.get('tasks', {})
    for idx, key in enumerate(sorted(tasks, key=int)):
        t = tasks[key]
        conds = None
        if t.get('nexttasks', {}) and t['type'] == 'condition':
            conds = []
            for label, targets in t['nexttasks'].items():
                for tgt in targets:
                    conds.append(ConditionBranch(option=label,
                                                 next_step=tasks[tgt]['taskid'],
                                                 condition=None))
        next_steps = []
        if not conds:
            for tgt in t.get('nexttasks', {}).get('#none#', []):
                next_steps.append(tasks[tgt]['taskid'])

        step = Step(
            id=t['taskid'],
            name=t['task']['name'],
            type=infer_xsoar_step_type(t),
            description=t['task'].get('description'),
            action=t['task'].get('scriptName'),
            conditions=conds,
            next_steps=next_steps,
            inputs=t.get('scriptarguments') or {},
            outputs=None,
            metadata={
                'xsoar_type': t['type'],
                'view': t.get('view'),
                'raw_task': t
            }
        )
        steps.append(step)

    return LambdaPlaybook(
        id=data.get('id'),
        name=data.get('name'),
        description=data.get('description'),
        steps=steps
    )


# xsoar_exporter.py
from internal_model import LambdaPlaybook, Step
import json
import ruamel.yaml

def calculate_view(idx: int, depth: int) -> str:
    x = depth * 200 + 50
    y = idx * 150 + 50
    return json.dumps({"position": {"x": x, "y": y}})

def depth_of(step: Step, steps_by_id: dict, memo=None) -> int:
    memo = memo or {}
    if step.id in memo:
        return memo[step.id]
    children = getattr(step, "next_steps", None) or []
    if not children:
        memo[step.id] = 0
    else:
        depths = []
        for child_id in children:
            child = steps_by_id.get(child_id)
            if child:
                depths.append(depth_of(child, steps_by_id, memo))
        memo[step.id] = max(depths, default=0) + 1
    return memo[step.id]

def export_xsoar(playbook: LambdaPlaybook) -> dict:
    tasks = {}
    step_id_to_task_id = {step.id: str(idx) for idx, step in enumerate(playbook.steps)}
    steps_by_id = {step.id: step for step in playbook.steps}

    XSOAR_TYPES = {
        "action": "regular",
        "condition": "condition",
        "manual": "condition",
        "start": "start",
        "title": "title",
        "subplaybook": "playbook"
    }

    for idx, step in enumerate(playbook.steps):
        task_id = str(idx)
        task_type = XSOAR_TYPES.get(step.type, "regular")

        nexttasks = {}
        if step.conditions:
            for cond in step.conditions:
                raw = (cond.option or "").strip().lower()
                label = "#default#" if raw in ("", "default", "#default#") else cond.option
                tid = step_id_to_task_id.get(cond.next_step)
                if tid:
                    nexttasks.setdefault(label, []).append(tid)
        else:
            ids = [step_id_to_task_id[sid] for sid in (step.next_steps or []) if sid in step_id_to_task_id]
            nexttasks["#none#"] = ids

        task_obj = {
            "id": step.id,
            "version": -1,
            "name": step.name,
            "description": step.description or None,
            "scriptName": step.action or None,
            "type": task_type,
            "iscommand": bool(step.action),
            "brand": step.metadata.get("integration") or None,
        }
        if task_type == "playbook":
            task_obj["playbookName"] = step.metadata.get("playbookName")

        depth = depth_of(step, steps_by_id)

        tasks[task_id] = {
            "id": task_id,
            "taskid": step.id,
            "type": task_type,
            "task": task_obj,
            "scriptarguments": step.inputs or {},
            "nexttasks": nexttasks,
            "continueonerror": False,
            "skipunavailable": False,
            "quietmode": 0,
            "timertriggers": step.metadata.get("raw_arguments", {}).get("timertriggers", []),
            "view": calculate_view(idx, depth),
            "note": False,
            "ignoreworker": False,
        }

    starttaskid = next((step_id_to_task_id[s.id] for s in playbook.steps if s.type == "start"), "0")

    return {
        "id": playbook.id,
        "name": playbook.name,
        "version": -1,
        "description": playbook.description,
        "tasks": tasks,
        "starttaskid": starttaskid,
    }
