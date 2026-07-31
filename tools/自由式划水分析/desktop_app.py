#!/usr/bin/env python3
"""
Swim Stroke Analyzer - Windows desktop launcher (for PyInstaller packaging).

Loads backend/app.py (and src/*) as real files from disk rather than letting
PyInstaller compile them into its bytecode archive, so their existing
__file__-based path logic (ROOT, FRONTEND_BUILD_DIR, uploads/results folders)
keeps working unchanged whether run from source or from a frozen .exe.
"""

import importlib.util
import os
import sys
import threading
import webbrowser

PORT = 8080


def get_base_dir():
    if getattr(sys, "frozen", False):
        # onefile: extracted to a temp dir each run (sys._MEIPASS).
        # onedir: _MEIPASS is unset, use the folder next to the .exe.
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def open_browser():
    webbrowser.open(f"http://127.0.0.1:{PORT}")


def main():
    base_dir = get_base_dir()
    sys.path.insert(0, base_dir)

    app_module = load_module_from_path(
        "backend_app", os.path.join(base_dir, "backend", "app.py")
    )
    flask_app = app_module.app

    print("=" * 60)
    print(" Swim Stroke Analyzer")
    print("=" * 60)
    print(f"Starting at http://127.0.0.1:{PORT} ...")
    print("Close this window to stop the service.")
    print("")

    threading.Timer(1.5, open_browser).start()

    from waitress import serve

    serve(flask_app, host="127.0.0.1", port=PORT)


if __name__ == "__main__":
    main()
