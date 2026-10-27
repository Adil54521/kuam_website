import subprocess
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

cmd = [
    sys.executable,
    "manage.py",
    "dumpdata",
    "myapp.Page",
    "--indent",
    "2"
]

result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

with open("pages.json", "w", encoding="utf-8") as f:
    f.write(result.stdout)

if result.stderr:
    print("WARNINGS / ERRORS:")
    print(result.stderr)
else:
    print("✔ Экспорт завершён: pages.json")
