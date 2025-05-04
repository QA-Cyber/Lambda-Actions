# LambdaC – SOAR Playbook Converter CLI

LambdaC is a CLI tool that converts SOAR playbooks **to/from the Lambda-Actions standard**, enabling:

- Seamless platform migration
- Schema unification
- Reusability across XSOAR, FortiSOAR, and more

---

## 🚀 Usage

```bash
python cli.py convert <input_file> --vendor <vendor> [--ai-fallback] [--sdk-validate]
````

### Parameters:

| Argument         | Description                                                             |
| ---------------- | ----------------------------------------------------------------------- |
| `input_file`     | Path to your input file (YAML or JSON)                                  |
| `--vendor`       | Required source format: `xsoar`, `fortisoar`, or any custom name        |
| `--ai-fallback`  | If specified, uses AI to assist in parsing/exporting when unsupported   |
| `--sdk-validate` | If specified, runs `demisto-sdk validate` after generating XSOAR output |

---

## 📦 Example Commands

### Convert XSOAR to Lambda (default behavior)

```bash
python cli.py convert samples/xsoar-alert.yml --vendor xsoar
```

### Convert FortiSOAR to Lambda

```bash
python cli.py convert samples/fortisoar-alert.json --vendor fortisoar
```

### Use AI fallback for unknown vendor format

```bash
python cli.py convert samples/unknown-playbook.json --vendor sentinel --ai-fallback
```

### Convert XSOAR with SDK validation

```bash
python cli.py convert samples/xsoar-block-ip.yml --vendor xsoar --sdk-validate
```

---

## 🗂️ Output Structure

When you convert a playbook, LambdaC will:

* Save the **converted vendor-specific output** to:
  `Playbooks_Repo/<vendor>/<name>.json` *(or `.yml` if Lambda output)*

* Always save the **intermediate Lambda-Actions format** to:
  `Playbooks_Repo/lambda/<name>.yml`

* Maintain **cached AI transformations** in:
  `LambdaC/cache/<vendor>/`

### Example Folder Output:

```
Playbooks_Repo/
├── xsoar/
│   └── alert-response.json
├── fortisoar/
│   └── endpoint-block.json
├── lambda/
│   └── alert-response.yml
LambdaC/
└── cache/
    └── xsoar/
        └── <hash>.json
```

---

## 🔁 How It Works

1. **Parses input** using a native parser or AI (if `--ai-fallback` is set)
2. Converts to **Lambda-Actions schema**
3. Optionally exports to native vendor format (if applicable)
4. Writes to the proper folders for:

   * Vendor format
   * Lambda-Actions format
   * AI cache (if used)

---

## 🧠 Need Help?

See the [main README](../README.md) for more context about Lambda-Actions, goals, and playbook examples.

---

## ✅ Ready to use LambdaC?

Convert once. Deploy anywhere.