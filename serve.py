# serve.py

from waitress import serve
from KUAMWebSite.wsgi import application
from datetime import datetime

with open("bootlog.txt", "a", encoding="utf-8") as f:
    f.write(f"[{datetime.now()}] ✅ serve.py STARTED\n")

# 🔒 слушаем только локально (через Nginx)
serve(application, host='127.0.0.1', port=8001, threads=8)
