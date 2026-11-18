"""Expose DuckDB's native UI with a read-only attachment to the pipeline data."""
import os
from pathlib import Path
import signal
import socket
import subprocess
import time

import duckdb

from config import DUCKDB_PATH


def interrupt(signum, frame) -> None:
    raise KeyboardInterrupt


def main() -> int:
    if not DUCKDB_PATH.is_file():
        raise FileNotFoundError(
            f"Database not found at {DUCKDB_PATH}. Run the pipeline first "
            "using the same Compose project name."
        )

    catalog_path = Path(os.environ.get("UI_CATALOG_PATH", "/opt/ui/catalog.duckdb"))
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    signal.signal(signal.SIGTERM, interrupt)
    proxy = None
    con = duckdb.connect(str(catalog_path))
    try:
        database_path = str(DUCKDB_PATH).replace("'", "''")
        con.execute(f"ATTACH '{database_path}' AS injuries (READ_ONLY)")
        con.execute("LOAD ui")
        con.execute("CALL start_ui_server()")
        # DuckDB UI binds to loopback. Forward a container-network port to it.
        # TCP forwarding preserves the UI's streaming HTTP connections.
        # The extension starts its HTTP listener on a background thread.
        for attempt in range(50):
            try:
                with socket.create_connection(("localhost", 4213), timeout=1) as probe:
                    address = probe.getpeername()[0]
                    target = (
                        f"TCP6:[{address}]:4213"
                        if probe.family == socket.AF_INET6 else f"TCP4:{address}:4213"
                    )
                break
            except OSError:
                if attempt == 49:
                    raise
                time.sleep(0.1)
        proxy = subprocess.Popen([
            "socat",
            "TCP-LISTEN:4214,bind=0.0.0.0,reuseaddr,fork",
            target,
        ])
        print("DuckDB UI available at http://localhost:4213", flush=True)
        print("Read-only data attached as injuries.bronze and injuries.silver.", flush=True)
        return proxy.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        if proxy is not None and proxy.poll() is None:
            proxy.terminate()
            proxy.wait()
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
