# xsoar_parser.py
import ruamel.yaml
from internal_model import LambdaPlaybook, Step, ConditionBranch

def parse_xsoar_yaml(path: str) -> LambdaPlaybook:
    """
    Load a Cortex XSOAR playbook YAML and turn it into our internal LambdaPlaybook.
    """
    yaml = ruamel.yaml.YAML()
    with open(path, 'r') as f:
        data = yaml.load(f)

    steps = []
    tasks = data.get('tasks', {})
    # tasks are keyed "0","1",...
    for idx, key in enumerate(sorted(tasks, key=int)):
        t = tasks[key]
        # build conditions
        conds = None
        if t.get('nexttasks', {}) and t['type'] == 'condition':
            conds = []
            # XSOAR condition steps usually have nexttasks keyed by labels
            for label, targets in t['nexttasks'].items():
                for tgt in targets:
                    conds.append(ConditionBranch(option=label,
                                                 next_step=tasks[tgt]['taskid'],
                                                 condition=None))
        # linear (non-condition)
        next_steps = []
        if not conds:
            for tgt in t.get('nexttasks', {}).get('#none#', []):
                next_steps.append(tasks[tgt]['taskid'])

        step = Step(
            id=t['taskid'],
            name=t['task']['name'],
            type='WorkflowStep',            # FortiSOAR always uses WorkflowStep
            description=t['task'].get('description'),
            action=None,                    # we keep raw args under `inputs`
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
