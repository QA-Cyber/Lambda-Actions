# fortisoar_exporter.py
import json
from uuid import uuid4

def export_fortisoar(pb) -> dict:
    """
    Turn a LambdaPlaybook into the FortiSOAR JSON workflow schema.
    """
    # helper to pluck view coordinates
    def coord(meta, axis):
        v = meta.get('view')
        try:
            return int(ruamel.yaml.round_trip_load(v)['position'][axis])
        except:
            return 0

    # 1) Build 'steps' array
    fs_steps = []
    for s in pb.steps:
        fs_steps.append({
            "@type": "WorkflowStep",
            "name": s.name,
            "description": s.description,
            "arguments": s.inputs or {},
            "status": None,
            "top": str(coord(s.metadata, 'y')),
            "left": str(coord(s.metadata, 'x')),
            "stepType": s.metadata.get('stepType', '/api/3/workflow_step_types/PLACEHOLDER'),
            "group": None,
            "uuid": s.id
        })

    # 2) Build 'routes' array
    fs_routes = []
    by_id = {s.id: s for s in pb.steps}
    for s in pb.steps:
        # branching conditions first
        if s.conditions:
            for c in s.conditions:
                fs_routes.append({
                    "@type": "WorkflowRoute",
                    "name": f"{s.name} → {by_id[c.next_step].name} [{c.option}]",
                    "targetStep": f"/api/3/workflow_steps/{c.next_step}",
                    "sourceStep": f"/api/3/workflow_steps/{s.id}",
                    "label": c.option,
                    "isExecuted": False,
                    "group": None,
                    "uuid": str(uuid4())
                })
        # linear flows
        for tgt in (s.next_steps or []):
            fs_routes.append({
                "@type": "WorkflowRoute",
                "name": f"{s.name} → {by_id[tgt].name}",
                "targetStep": f"/api/3/workflow_steps/{tgt}",
                "sourceStep": f"/api/3/workflow_steps/{s.id}",
                "label": None,
                "isExecuted": False,
                "group": None,
                "uuid": str(uuid4())
            })

    # 3) Assemble top-level
    return {
        "@type": "Workflow",
        "triggerLimit": None,
        "name": pb.name,
        "aliasName": None,
        "tag": None,
        "description": pb.description,
        "isActive": True,
        "debug": False,
        "singleRecordExecution": False,
        "remoteExecutableFlag": False,
        "parameters": [inp['name'] for inp in (pb.metadata.get('inputs') or [])],
        "synchronous": False,
        "collection": "/api/3/workflow_collections/PLACEHOLDER",
        "versions": [],
        "triggerStep": f"/api/3/workflow_steps/{pb.steps[0].id}",
        "steps": fs_steps,
        "routes": fs_routes,
        "groups": [],
        "priority": None,
        "playbookOrigin": None,
        "isEditable": True,
        "uuid": pb.id,
        "owners": [],
        "isPrivate": False,
        "deletedAt": None,
        "recordTags": []
    }
