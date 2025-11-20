import os
import ast
import subprocess

PROJECT_DIR = "recallai_backend"   # your backend folder name

# Packages known to be part of the standard library (ignore these)
try:
    stdlibs = subprocess.check_output(
        ["python", "-c", "import sys; print('\\n'.join(sorted(sys.stdlib_module_names)))"]
    ).decode().split()
except Exception:
    stdlibs = []

imports = set()

def scan_file(path):
    with open(path, "r", encoding="utf-8") as f:
        node = ast.parse(f.read(), filename=path)
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                imports.add(n.module.split(".")[0])

# Scan all .py files in the backend
for root, _, files in os.walk(PROJECT_DIR):
    for file in files:
        if file.endswith(".py"):
            scan_file(os.path.join(root, file))

# Filter out stdlib
final = [pkg for pkg in imports if pkg not in stdlibs]

# Known mappings: Python package name -> pip package name
SPECIAL_MAP = {
    "pydantic_settings": "pydantic-settings",
    "psycopg2": "psycopg2-binary",
    "uvicorn": "uvicorn[standard]",
    "fastapi": "fastapi",
    "sqlalchemy": "sqlalchemy",
    "pgvector": "pgvector",
    "dotenv": "python-dotenv",
    "openai": "openai",
    "multipart": "python-multipart",
    "aiofiles": "aiofiles",
}

pip_packages = []

for pkg in final:
    if pkg in SPECIAL_MAP:
        pip_packages.append(SPECIAL_MAP[pkg])
    else:
        pip_packages.append(pkg)

pip_packages = sorted(set(pip_packages))

# Write to requirements.txt
with open("requirements.generated.txt", "w") as f:
    f.write("\n".join(pip_packages))

print("Generated requirements.generated.txt with:")
for pkg in pip_packages:
    print(" -", pkg)
