# LambdaC – SOAR Playbook Converter

**LambdaC** is a vendor-agnostic CLI tool for converting SOAR playbooks between different platforms using the [Lambda-Actions](https://github.com/YOUR_ORG/Lambda-Actions) intermediate schema.

It supports:

* 🔁 Conversion from XSOAR, FortiSOAR, and AI-parsed formats to Lambda-Actions
* 🔄 Export back into XSOAR and FortiSOAR formats
* 🧠 AI fallback support for unknown vendor formats
* 🧪 Optional `demisto-sdk` validation for XSOAR exports

---

## ⚙️ Prerequisites

* Python 3.10 or higher

* Install dependencies:

  ```bash
  pip install -r requirements.txt
  ```

* Optional: Install `demisto-sdk` for validation

  ```bash
  pip install demisto-sdk
  ```

---

## 🧱 Directory Structure

LambdaC expects to be inside a repo like:

```
Lambda-Actions/
├── LambdaC/
│   ├── lambdaC.py
│   ├── exporters/
│   ├── parsers/
│   ├── transformers/
│   ├── validators/
│   └── cache/
├── Playbooks_Repo/
│   ├── xsoar/
│   ├── fortisoar/
│   └── lambda/
├── samples/
└── ...
```

---

## 🚀 How to Use

```bash
python lambdaC.py --input-file <path> --input-vendor <vendor> --output-vendor <vendor> [--ai-fallback] [--sdk-validate]
```

### Example Commands:

#### ✅ Convert XSOAR to FortiSOAR + Lambda:

```bash
python lambdaC.py --input-file samples/prod_sample_xsoar.yml --input-vendor xsoar --output-vendor fortisoar
```

#### ✅ Convert FortiSOAR to XSOAR + Lambda:

```bash
python lambdaC.py --input-file samples/prod_sample_fsoar2.json --input-vendor fortisoar --output-vendor xsoar
```

#### ✅ Convert unknown format using AI:

```bash
python lambdaC.py --input-file samples/custom_playbook.json --input-vendor sentinel --output-vendor lambda --ai-fallback
```

#### ✅ Validate generated XSOAR output with demisto-sdk:

```bash
python lambdaC.py --input-file samples/block-ip.yml --input-vendor xsoar --output-vendor xsoar --sdk-validate
```

---

## 📤 Output Behavior

* Vendor-formatted playbooks (e.g. FortiSOAR, XSOAR) are saved to:

  ```
  Playbooks_Repo/<vendor>/<original-name>.json|.yml
  ```

* **Always** generates a Lambda-Actions YAML (intermediate) to:

  ```
  Playbooks_Repo/lambda/LA - <Playbook Name>.yml
  ```

* Skips overwriting output files **if existing content differs** to avoid accidental loss.

* AI fallback transformations are cached under:

  ```
  LambdaC/cache/<vendor>/
  ```

---

## 🧾 Output Example

After running a conversion, you’ll get:

```
Playbooks_Repo/
├── xsoar/
│   └── prod_sample_fsoar2.yml
├── fortisoar/
│   └── prod_sample_xsoar.json
├── lambda/
│   └── LA - Action_-_Domain_-_Block_(Indicator).yml
LambdaC/
└── cache/
    └── fortisoar/
        └── [cached hash].json
```

---

## 🧠 Notes

* The `--output-vendor` controls only the **main target format**. The Lambda-Actions YAML is always generated unless you specify `output-vendor=lambda`, in which case only the Lambda YAML is saved.
* Filenames are derived from input filenames or playbook names, sanitized and prefixed with `LA -` for Lambda exports.

---

## ✅ Ready to Use?

LambdaC bridges platforms, enhances reusability, and accelerates SOAR deployments.

Convert once. Deploy anywhere.