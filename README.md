# Lambda-Actions - Generic Standard for SOAR Playbooks

<p align="center">
  <a href="https://github.com/Troybado/Lambda-Actions">
    <img width="600" alt="Lambda-Actions Logo" src="./images/Lambda-Logo-White.png">
  </a>
</p>

  

Lambda-Actions is an open standard that helps security teams write and share SOAR Playbooks using a simple, portable format that is designed to fit all SOAR Platforms like Cortex XSOAR, FortiSOAR, Microsoft Sentinel (Logic Apps), etc..

Lambda-Actions is for SOAR Playbooks, like what Sigma is for detections, & what Snort is for network traffic...

Lambda currently offer three types of Playbooks:
* [Generic Actions](./playbooks/generic-actions) – Are generic Playbooks (e.g: IP Enrichment)
* [Response Actions](./playbooks/incident-response-actions) – Are specific response Playbooks to mitigate incidents (e.g: IOC blocking)
* [Use Cases](./playbooks/use-cases) – comprehensive Playbooks to address a Security Use Case (e.g: Password Spray Detected)

## 🚨 Why Lambda-Actions Exists

Security teams struggle with Playbook **portability**, **interoperability**, and **standardization** across SOAR platforms.

Today:
- Each SOAR platform (FortiSOAR, Sentinel (Logic Apps), XSOAR, etc.) uses its own **proprietary format**.
- Sharing or reusing automation Playbooks across tools is **manual and time-consuming**.
- Switching tools or collaborating across teams = **rewriting automation playbooks from scratch**.

#### This Creates
- ❌ **Vendor lock-in** — migrating to another tool is costly due to incompatible Playbooks  
- ❌ **Tooling silos** — hard to collaborate across different SOARs  
- ❌ **Duplicated effort** — same logic rebuilt for each platform

#### Lambda-Actions solves these problems by aiming to:

- ✅ **Use easy, readable Playbook standard** — skip the GUIs and custom formats
- ✅ **Develop fast** — reuse community Playbooks or create your own
- ✅ **Share and collaborate** — frictionless Playbook portability
- ✅ **Write once, convert anywhere** — supports XSOAR, Sentinel (Logic Apps), FortiSOAR.

The following diagram shows how Lambda-Actions standardizes Playbooks and enables cross-platform SOAR integration:

<p align="center">
  <a href="https://github.com/Troybado/Lambda-Actions">
    <img width="800" alt="Lambda-Actions Logo" src="./images/Lambda-Flow.png">
  </a>
</p>

---

## 📚 Getting Started & Documentation

- **[Lambda-Actions Playbooks](./playbooks/)** – Browse ready-to-use Playbooks  
- **[How to Create Lambda Action Playbooks](./docs/playbook-Creation-Guide.md)** – Step-by-step authoring guide  

## 🔨 LambdaC: The Playbook Converter (Coming Soon)

Use the CLI tool **LambdaC** to convert Lambda Playbooks to:

- Cortex XSOAR  
- FortiSOAR  
- Sentinel (Logic Apps)

and vice versa..

📖 [LambdaC Tool Documentation](./tools/lambdac/README.md)

## 🤝 Contribute to Lambda-Actions

We welcome contributions from engineers, analysts, and automation pros!

- 📥 Submit Playbooks
- 🛠️ Improve the spec or tooling
- 💬 Propose new features

📖 [Open an Issue](https://github.com/Troybado/Lambda-Actions/issues/new/choose)

## Owner

- [Qusai A. (@Qusai A.)](https://github.com/QA-Cyber)
