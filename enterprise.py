import subprocess
import sys
import os
import time
import webbrowser
import re
import json
# Load config.json
with open("settings.json", "r") as f:
    config = json.load(f)
# --------------------------------------------------
# Usage: python setup_splunk_container.py <container_name> <network_name> <port>
# Example: python setup_splunk_container.py cm splunk-net 8000
# --------------------------------------------------
docker_exe = config["docker"]["docker_exe"]
splunk_tgz_path = config["splunk"]["enterprise"]["splunk_tgz_path"]
splunk_user = config["splunk"]["enterprise"]["admin_username"]
splunk_pass = config["splunk"]["enterprise"]["admin_password"]

# === Read arguments ===
if len(sys.argv) < 4:
    print("Usage: python setup_splunk_container.py <container_name> <network_name> <port>")
    sys.exit(1)

container_name = sys.argv[1]
network_name = sys.argv[2]
port = sys.argv[3]

# === Load environment variables ===

match = re.search(r"([^\\\/]+\.tgz)$", splunk_tgz_path)
if not match:
    raise ValueError("Could not extract Splunk package filename from path!")
splunk_filename = match.group(1)

print(f"Detected Splunk package file: {splunk_filename}")

# === Helper function ===
def run(cmd, check=True, capture=False, text=True, shell=False):
    print(f"\n>>> Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    return subprocess.run(cmd, check=check, text=text, shell=shell, capture_output=capture)

# === 1. Create container ===
run([docker_exe, "run", "-dit", "--name", container_name, "--network", network_name, "-p", f"{port}", "ubuntu"])

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

# === 6. Add OPTIMISTIC_ABOUT_FILE_LOCKING ===
run([docker_exe, "exec", "-w", "/opt/splunk/etc", container_name,
     "bash", "-c", 'echo "OPTIMISTIC_ABOUT_FILE_LOCKING = 1" >> splunk-launch.conf'])

# === 7. Start Splunk and auto-provide credentials ===
# Splunk’s first start prompts for admin user/pass — we’ll feed these automatically.
splunk_start_cmd = (
    f"echo -e '{splunk_user}\\n{splunk_pass}\\n{splunk_pass}\\n' | "
    f"/opt/splunk/bin/splunk start --accept-license"
)

print("\n>>> Starting Splunk and providing credentials automatically...")
run([docker_exe, "exec", "-w", "/opt/splunk/bin", container_name, "bash", "-c", splunk_start_cmd])

print("\n✅ Done! Splunk started successfully inside container:", container_name)