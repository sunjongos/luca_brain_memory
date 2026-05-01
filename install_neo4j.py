import os
import urllib.request
import zipfile
import sys

def download_and_extract(url, extract_to):
    print(f"Downloading {url}...")
    filename, _ = urllib.request.urlretrieve(url)
    print(f"Extracting to {extract_to}...")
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(filename)

base_dir = os.path.dirname(os.path.abspath(__file__))
neo4j_env_dir = os.path.join(base_dir, "neo4j_env")
os.makedirs(neo4j_env_dir, exist_ok=True)

# URL of OpenJDK 17 (Windows x64) - Microsoft Build of OpenJDK
jdk_url = "https://aka.ms/download-jdk/microsoft-jdk-17.0.10-windows-x64.zip"
# URL of Neo4j Community
neo4j_url = "https://dist.neo4j.org/neo4j-community-5.18.1-windows.zip"

print("Starting Neo4j Portable Setup...")
download_and_extract(jdk_url, neo4j_env_dir)
download_and_extract(neo4j_url, neo4j_env_dir)

# Find directories
jdk_dir = [d for d in os.listdir(neo4j_env_dir) if "jdk" in d.lower()][0]
neo4j_dir = [d for d in os.listdir(neo4j_env_dir) if "neo4j" in d.lower()][0]

jdk_path = os.path.join(neo4j_env_dir, jdk_dir)
neo4j_path = os.path.join(neo4j_env_dir, neo4j_dir)

# Modify neo4j.conf to disable auth for local dev
conf_path = os.path.join(neo4j_path, "conf", "neo4j.conf")
with open(conf_path, "a", encoding="utf-8") as f:
    f.write("\n# Disable authentication for local dev\n")
    f.write("dbms.security.auth_enabled=false\n")
    f.write("server.default_listen_address=0.0.0.0\n")

# Create start script
bat_path = os.path.join(neo4j_env_dir, "start_neo4j.bat")
with open(bat_path, "w") as f:
    f.write('@echo off\n')
    f.write(f'set JAVA_HOME=%~dp0{jdk_dir}\n')
    f.write(f'set PATH=%JAVA_HOME%\\bin;%PATH%\n')
    f.write(f'cd %~dp0{neo4j_dir}\\bin\n')
    f.write(f'neo4j.bat console\n')

print("✅ Neo4j and JDK 17 downloaded and configured successfully!")
print(f"Run {bat_path} to start Neo4j.")
