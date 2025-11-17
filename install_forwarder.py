import subprocess
import sys
import os
import time
import re
import json
# Load config.json
with open("settings.json", "r") as f:
    config = json.load(f)

if len(sys.argv) < 2:
    print("Usage: python setup_splunk_container.py <container_name>")
    sys.exit(1)

container_name = sys.argv[1]
#=== Config ====
docker_exe = config["docker"]["docker_exe"]
splunk_tgz_path = config["splunk"]["forwarder"]["splunk_tgz_path"]
splunk_user = config["splunk"]["forwarder"]["admin_username"]
splunk_pass = config["splunk"]["forwarder"]["admin_password"]

match = re.search(r"([^\\\/]+\.tgz)$", splunk_tgz_path)
if not match:
    raise ValueError("Could not extract Splunk package filename from path!")
splunk_filename = match.group(1)

print(f"Detected Splunk package file: {splunk_filename}")
# === Helper function ===
def run(cmd, check=True, capture=False, text=True, shell=False):
    print(f"\n>>> Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return subprocess.run(cmd, check=check, text=text, shell=shell, capture_output=capture)

# === 2. Copy Splunk package ===
run([docker_exe, "cp", splunk_tgz_path, f"{container_name}:/opt"])

# === 3. Install dependencies ===
run([docker_exe, "exec", container_name, "apt", "update"])
run([docker_exe, "exec", container_name, "apt", "install", "-y",
     "apt-utils", "nano", "vim", "curl", "wget", "net-tools", "iputils-ping",
     "procps", "unzip", "zip", "tar", "git", "lsb-release", "dnsutils", "sudo"])
run([docker_exe, "exec", container_name, "apt", "update"])

# === 4. Extract Splunk ===
run([docker_exe, "exec", "-w", "/opt", container_name, "tar", "-xvzf",  splunk_filename])

# === 5. Remove tar file ===
run([docker_exe, "exec", "-w", "/opt", container_name, "rm",  splunk_filename])

# === 7. Start Splunk and auto-provide credentials ===
# Splunk’s first start prompts for admin user/pass — we’ll feed these automatically.
splunk_start_cmd = (
    f"echo -e '{splunk_user}\\n{splunk_pass}\\n{splunk_pass}\\n' | "
    f"/opt/splunkforwarder/bin/splunk start --accept-license"
)

print("\n>>> Starting Splunk and providing credentials automatically...")
run([docker_exe, "exec", "-w", "/opt/splunkforwarder/bin", container_name, "bash", "-c", splunk_start_cmd])

print("\nDone! Splunk started successfully inside container:", container_name)
