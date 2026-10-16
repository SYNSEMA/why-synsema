"""Helper module: formats numbers. It stands for any dependency the ETL imports.
It also reports what it COULD do with the process permissions (booleans only, never contents)."""
import os, socket

def capabilities():
    can_env = os.path.exists(".env") and len(open(".env").read()) > 0
    try:
        socket.create_connection(("example.com", 443), timeout=5).close(); net = True
    except OSError:
        net = False
    return {"read .env": can_env, "reach an undeclared host": net, "environment variables visible": len(os.environ)}

def round1(x, n=1):
    return round(x, n)
