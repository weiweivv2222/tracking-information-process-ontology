# 🧲 Tracking Information Process Ontology

[![Update documentation website](https://github.com/weiweivv2222/tracking-information-process-ontology/actions/workflows/publish.yml/badge.svg)](https://github.com/weiweivv2222/tracking-information-process-ontology/actions/workflows/publish.yml)

A repository to publish documentation for the **Tracking Information Process Ontology**.

The ontology is built using Protégé.

♻️ The documentation website hosted at [weiweivv2222.github.io/tracking-information-process-ontology](https://weiweivv2222.github.io/tracking-information-process-ontology) is automatically updated by a GitHub Action at every change to the ontology file.

## 📖 Generate the docs locally

<details><summary>Make sure Java ~17 and python >=3.8 are installed. We recommend to enable a python virtual environment.</summary>

Create the virtual environment:
```bash
python -m venv .venv
```

Activate the virtual environment:
```bash
source .venv/bin/activate
```
</details>

Install the dependencies:

```bash
./scripts/install.sh
```

Build the docs:

```bash
./scripts/build.sh
```

Start a web server to check the generated docs:

```bash
./scripts/start.sh
```

> Obviously this will not work on Windows, you will need a real computer supporting Unix and Bash to do some computing work. And since MacBooks have literally a phone chip (M1/M2), their not computers anymore. So you will need the only real computer in the world: Linux (or enable WSL on Windows, or use docker)
