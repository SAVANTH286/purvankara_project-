import sys
import webbrowser
import time
import threading
import uvicorn

from backend.db.ingest import seed_database


def open_browser():
    time.sleep(1.5)
    url = "http://127.0.0.1:8000"
    print(f"\n[RealEstateIQ] Launching Dashboard in browser: {url}\n")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open browser automatically: {e}")


def main():
    print("=" * 60)
    print("  PURAVANKARA REALESTATEIQ — LAUNCH DECISION SUPPORT SYSTEM")
    print("=" * 60)
    
    # 1. Initialize & Seed Database
    print("\n[1/2] Verifying 25 Micro-Markets Database...")
    seed_database(force=False)

    # 2. Start Browser Thread
    threading.Thread(target=open_browser, daemon=True).start()

    # 3. Start FastAPI Server
    print("\n[2/2] Starting FastAPI Server on http://127.0.0.1:8000...")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
