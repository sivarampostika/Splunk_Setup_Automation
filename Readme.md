# 🧠 Splunk Setup Automation

This repository provides Python scripts to automate the setup and management of **Splunk Enterprise** and **Universal Forwarders** in Docker containers.

---

## ⚙️ Setup

1. Edit the **`settings.json`** file according to your environment.
2. Update the **username** and **password** fields before running any scripts.

---

## 🚀 Usage

### 🧩 Complete Splunk Docker Setup

#### **enterprise.py**

Used to install various **Splunk Enterprise components**, such as:

* Search Head
* Indexer
* Deployment Server
* Deployer
* Heavy Forwarder
* Cluster Master
* License Master

**Run Command:**

```bash
python enterprise.py <container_name> <network_name> <port>
```

**Example:**

```bash
python enterprise.py search-head splunk-net 8001:8000
```

---

#### **forwarder.py**

Used to install **Splunk Universal Forwarders**.

**Run Command:**

```bash
python forwarder.py <container_name> <network_name>
```

**Example:**

```bash
python forwarder.py Linux-uf splunk-net
```

---

### 🛠️ Installation Only (No Container Setup)

#### **install_enterprise.py**

Installs Splunk Enterprise in an existing container.

**Run Command:**

```bash
python install_enterprise.py <container_name>
```

---

#### **install_forwarder.py**

Installs Splunk Universal Forwarder in an existing container.

**Run Command:**

```bash
python install_forwarder.py <container_name>
```

---

## 📁 Directory Structure (Recommended)

```
splunk-setup-automation/
│
├── enterprise.py
├── forwarder.py
├── install_enterprise.py
├── install_forwarder.py
├── settings.json
└── README.md
```

---

## 🧩 Notes

* Ensure Docker is installed and running.
* The network name (e.g., `splunk-net`) must exist before running the scripts.
* Use appropriate ports when exposing the Splunk web interface.
