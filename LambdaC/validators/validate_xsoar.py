# validators/validate_xsoar.py
import jsonschema
import json

XSOAR_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Cortex XSOAR Playbook",
    "type": "object",
    "required": ["id", "name", "version", "starttaskid", "tasks"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "version": {"type": "integer"},
        "description": {"type": ["string", "null"]},
        "starttaskid": {"type": "string"},
        "tasks": {
            "type": "object",
            "patternProperties": {
                "^[0-9]+$": {  # Task identifiers are typically numeric strings
                    "type": "object",
                    "required": ["id", "taskid", "type", "task"],
                    "properties": {
                        "id": {"type": "string"},
                        "taskid": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": ["start", "regular", "condition", "title", "playbook"]
                        },
                        "task": {
                            "type": "object",
                            "required": ["id", "name", "type", "iscommand", "version"],
                            "properties": {
                                "id": {"type": "string"},
                                "version": {"type": "integer"},
                                "name": {"type": "string"},
                                "description": {"type": ["string", "null"]},
                                "scriptName": {"type": ["string", "null"]},
                                "type": {
                                    "type": "string",
                                    "enum": ["start", "regular", "condition", "title", "playbook"]
                                },
                                "iscommand": {"type": "boolean"},
                                "brand": {"type": ["string", "null"]},
                                "script": {"type": ["string", "null"]},
                                "playbookName": {"type": ["string", "null"]}
                            },
                            "additionalProperties": True
                        },
                        "nexttasks": {
                            "type": "object",
                            "patternProperties": {
                                "^.*$": {  # This is for task navigation to other tasks
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "additionalProperties": False
                        },
                        "conditions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["label", "condition"],
                                "properties": {
                                    "label": {"type": "string"},
                                    "condition": {"type": "array"}
                                },
                                "additionalProperties": True
                            }
                        },
                        "scriptarguments": {"type": "object"},
                        "separatecontext": {"type": "boolean"},
                        "continueonerrortype": {"type": "string"},
                        "continueonerror": {"type": "boolean"},
                        "skipunavailable": {"type": "boolean"},
                        "quietmode": {"type": ["integer", "string"]},
                        "reputationcalc": {"type": "number"},
                        "isoversize": {"type": "boolean"},
                        "isautoswitchedtoquietmode": {"type": "boolean"},
                        "timertriggers": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["fieldname", "action"],
                                "properties": {
                                    "fieldname": {"type": "string"},
                                    "action": {"type": "string"}
                                },
                                "additionalProperties": True
                            }
                        },
                        "view": {
                            "oneOf": [
                                {"type": "string"},
                                {"type": "object"}
                            ]
                        },
                        "note": {"type": "boolean"},
                        "ignoreworker": {"type": "boolean"},
                        "loop": {
                            "type": "object",
                            "properties": {
                                "iscommand": {"type": "boolean"},
                                "exitCondition": {"type": "string"},
                                "wait": {"type": "number"},
                                "max": {"type": "number"}
                            },
                            "additionalProperties": True
                        }
                    },
                    "additionalProperties": True
                }
            },
            "additionalProperties": False
        },
        "inputs": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["key", "value", "required", "description"],
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "object"},
                    "required": {"type": "boolean"},
                    "description": {"type": "string"}
                },
                "additionalProperties": True
            }
        },
        "outputs": {
            "type": "array",
            "items": {"type": "object"}
        }
    },
    "additionalProperties": False
}

def validate_xsoar_playbook(playbook_json: dict) -> None:
    """
    Validate a Cortex XSOAR playbook JSON against the enhanced XSOAR_SCHEMA.
    Raises jsonschema.ValidationError if the playbook is invalid.
    """
    jsonschema.validate(instance=playbook_json, schema=XSOAR_SCHEMA)