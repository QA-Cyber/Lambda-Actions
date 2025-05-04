# Lambda-Actions - Generic Standard & Convertor for Security Playbooks

<p align="center">
    <a href="https://github.com/QA-Cyber/Lambda-Actions"></a>
  <img width="600" src="./documentations/images/Lambda-Logo-White.png" alt="Lambda Logo">
</p>

Lambda-Actions is an open standard to define **portable, platform-agnostic SOAR playbooks** — Lambda-Actions is for Security Actions, much like how [Sigma](https://github.com/SigmaHQ/sigma) is for Detections.


## 🚨 Why Lambda-Actions Exists

Lambda-Actions aims to eliminate vendor lock-in and fragmentation across automation platforms like:
- SOAR Platforms (ex: XSOAR, FortiSOAR, Phantom, Resilient)
- Automation Platforms (ex: Logic Apps, Zapier)
- Custom-built orchestrators

The following diagram shows how Lambda-Actions standardizes Playbooks and enables cross-platform SOAR integration:

<p align="center">
  <a href="https://github.com/QA-Cyber/Lambda-Actions">
    <img width="800" alt="Lambda-Actions Logo" src="./documentations/images/Lambda-Flow.png">
  </a>
</p>

---

## ✨ Main Features
All playbooks in this repository are structured for **direct import into your SOAR platform**, removing the friction from tool migration or cross-vendor automation.

- 💡 **Lambda-Actions Format** – A YAML-based generic schema for modeling playbooks that is easy to read, write, and share.
- 📁 **Playbooks_Repo/** – Due to convertor, this repo would host large number of standarized security playbooks, allowing users to browse and reuse existing playbooks for different platforms: All ready to import directly into their respective SOAR platforms.
- 🔄 **LambdaC Tool** – Convertor between popular SOAR platforms and also Lambda.
  - 🧠 **Intelligent Conversions** – Currently supports vice versa betwnee XSOAR, FortiSOAR & Lambda. For unsupported SOAR formats it uses intelligent transformation logic to convert to Lambda.

<p align="center">
  <img width="800" src="./documentations/images/Lambda-Flow.png" alt="Lambda Flow Diagram">
</p>

---

## [`Lambda Schema & Documentation`](./documentations)
### Schema references, authoring guides, and best practices

---
## 🌀[`LambdaC`](./LambdaC/README.md)
### CLI tool to convert SOAR playbooks to/from Lambda-Actions

---

## 📚[`Playbooks_Repo`](./Playbooks_Repo)
### Central folder with converted playbooks per vendor & Lambda

---

## Contribute to Lambda-Actions

- 🛠️ Improve the spec, the LambdaC converter, or propose features via [Issues](https://github.com/QA-Cyber/Lambda-Actions/issues/new/choose) tab.


## Owner

- [Qusai A. (@Qusai A.)](https://github.com/QA-Cyber)
