## Table of Contents

- [Lambda Actions YAML Schema](#lambda-actions-yaml-schema)
- [Schema Documentation](#schema-documentation)
  - [Metadata](#metadata)
  - [Triggers](#triggers)
  - [Steps](#steps)
  - [Inputs](#inputs)
  - [Outputs](#outputs)
  - [Metadata for Conversion](#metadata-for-conversion)
- [Schema Design Principles](#schema-design-principles)
- [Lambda-Actions Schema Source File](#Lambda-Actions-Schema-Source-File)
- [Lambda-Actions Samples](#Lambda-Actions-Samples)
- [LambdaC Tool Documentation](#lambdac-tool-documentation)

---

## Lambda Actions YAML Schema

<details>
<summary>📄 Click to Expand: View the Full YAML Schema</summary>

```yaml
# Top-level metadata for Lambda-Action playbook identification and management
id: STRING
name: STRING
description: STRING

# Trigger definition
trigger:
  type: ENUM(manual | scheduled | event)
  schedule: STRING
  event:
    source: STRING
    on: ENUM(create | update)
    fields: [STRING]
    filters: MAP

# Steps definition
steps:
  - id: STRING
    type: ENUM(action | condition | subplaybook | manual | script | task)
    description: STRING

    action: STRING
    connector: STRING (optional)
    inputs: MAP
    outputs: MAP

    conditions:
      - if: STRING
        then: STRING
        else: STRING

    subplaybooks: [STRING]
    parallel: BOOLEAN
    inputs: MAP
    outputs: MAP

    instructions: STRING
    timeout: INTEGER
    escalation:
      notify: [STRING]
      escalate_after: INTEGER

    runtime: ENUM(python | javascript | lua)
    script_content: STRING
    inputs: MAP
    outputs: MAP

    task_definition:
      type: STRING
      parameters: MAP
      description: STRING
      outputs: MAP

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

# Metadata for conversion purposes
metadata:
  vendor_mappings: MAP
```

</details>

---

## Schema Documentation

### Metadata

- **`id`**: Unique identifier for the playbook.
- **`name`**: Descriptive title for the playbook.
- **`description`**: Purpose and context of the playbook.

### Triggers

Defines how the playbook is initiated:

- **`manual`**: Initiated manually by an analyst.
- **`scheduled`**: Initiated by a defined schedule (e.g., cron).
- **`event`**: Initiated by changes to an external or internal record.
  - `on: create` triggers on new object creation.
  - `on: update` triggers only when specific `fields` are modified.

**Example:**
```yaml
trigger:
  type: event
  event:
    source: indicators_module
    on: create
    filters:
      typeofindicator:
        - "Domain"
        - "IP Address"
      reputation:
        or:
          - "To be Determined"
          - null
```

### Steps

All logic is modeled as sequential or conditional steps.

#### Action Step
Executes operations via integrations or platform actions.
```yaml
- id: enrich-indicator
  type: action
  description: Run enrichment for indicator
  action: enrich_ioc
  inputs:
    indicator_value: "{{ inputs.indicator_value }}"
    indicator_type: "{{ inputs.indicator_type }}"
  outputs:
    reputation: "{{ result.reputation }}"
```

#### Condition Step
Performs branching logic based on inputs or previous results.
```yaml
- id: check-verdict
  type: condition
  description: Decide based on verdict
  conditions:
    - if: "{{ steps.enrich-indicator.outputs.reputation == 'Malicious' }}"
      then: block-indicator
      else: exit-clean
```

#### Subplaybook Step
Invokes other playbooks for reuse.
```yaml
- id: run-sub-playbooks
  type: subplaybook
  description: Execute enrichment playbooks
  subplaybooks: "{{ steps.get-playbooks.outputs.playbook_list }}"
  parallel: true
  inputs:
    indicator_value: "{{ inputs.indicator_value }}"
```

#### Manual Step
Requires human approval.
```yaml
- id: approve-deletion
  type: manual
  instructions: "Approve indicator removal."
  timeout: 15
  escalation:
    notify: ["admin"]
    escalate_after: 10
```

#### Script Step
Executes custom code.
```yaml
- id: calculate-score
  type: script
  runtime: python
  script_content: |
    def run(input):
      return {"score": 95 if input == 'IP' else 80}
  inputs:
    type: "{{ inputs.indicator_type }}"
  outputs:
    score: "result.score"
```

#### Task Step
Abstract task block for complex integrations.
```yaml
- id: call-custom-api
  type: task
  task_definition:
    type: api_call
    parameters:
      url: "https://api.cti.io"
      method: "GET"
    description: "Custom API call"
    outputs:
      data: "result.data"
```

### Inputs

Playbook-level parameters provided at runtime.
```yaml
inputs:
  - name: indicator_value
    description: Raw indicator to be enriched
  - name: indicator_type
    description: Indicator classification
```

### Outputs

Final result values passed outside the playbook.
```yaml
outputs:
  - name: reputation
    description: Final verdict from enrichment
    value: "{{ steps.enrich-indicator.outputs.reputation }}"
```

### Metadata for Conversion

Vendor-specific mapping configuration. Not required if you're not running the LambdaC.
```yaml
metadata:
  vendor_mappings:
    xsoar:
      playbook_type: indicator
    sentinel:
      category: threat_intel
```
---

## Schema Design Principles

- **Vendor-Neutral**: Supports logic across platforms.
- **Minimalist**: Only essential logic and metadata included.
- **Composable**: Encourages modular and reusable design.
- **Declarative**: Describes what to do, not how to execute.
---

## Lambda-Actions Schema Source File

Official YAML schema file used for validation and playbook authoring.

[Lambda Schema YAML → docs/Lambda-Schema.yml](./Lambda-Schema.yml)

---

## Lambda-Actions Samples

Official Lambda-Actions playbooks published.

[Lambda-Actions → playbooks/](././playbooks)

---

## LambdaC Tool Documentation

Detailed instructions on using LambdaC for converting Lambda-Actions playbooks into specific vendor formats.

[LambdaC Guide → docs/LambdaC-Guide.md](./LambdaC-Guide.md)

---
