#!/usr/bin/env python3
# aion_taxonomy/scripts/refresh_sensitivities.py
# Weekly refresh: fetch latest market data → recompute 90-day rolling correlations
# Can be run manually or via cron: 0 6 * * 1  # Every Monday 6 AM

import sys
import time
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent

def main():
    print("=" * 60)
    print("AION Weekly Sensitivity Refresh")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)

    # Step 1: Fetch latest Yahoo Finance data
    print("\n[1/3] Fetching latest Yahoo Finance sector data...")
    fetch_script = SCRIPT_DIR / "fetch_meta_data.py"
    if fetch_script.exists():
        import subprocess
        result = subprocess.run(
            [sys.executable, str(fetch_script)],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            print(f"  ✗ fetch_meta_data.py failed: {result.stderr[:200]}")
            return False
        print("  ✓ Yahoo Finance data updated")
        # Print last 5 lines of output
        lines = result.stdout.strip().split('\n')
        for line in lines[-5:]:
            print(f"    {line}")
    else:
        print(f"  ⚠ {fetch_script} not found, skipping")

    time.sleep(5)

    # Step 2: Fetch latest G-Sec yield data (batched XHR)
    print("\n[2/3] Fetching latest G-Sec 10Y yield data...")
    scrape_script = SCRIPT_DIR / "scrape_gsec_yield.py"
    if scrape_script.exists():
        import subprocess
        result = subprocess.run(
            [sys.executable, str(scrape_script)],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            print(f"  ⚠ scrape_gsec_yield.py failed: {result.stderr[:200]}")
            print("  → Continuing with existing G-Sec data")
        else:
            print("  ✓ G-Sec yield data updated")
            lines = result.stdout.strip().split('\n')
            for line in lines[-3:]:
                print(f"    {line}")
    else:
        print(f"  ⚠ {scrape_script} not found, skipping")

    time.sleep(5)

    # Step 3: Recompute sensitivities
    print("\n[3/3] Recomputing 90-day rolling correlations...")
    update_script = SCRIPT_DIR / "update_sensitivities.py"
    if update_script.exists():
        import subprocess
        result = subprocess.run(
            [sys.executable, str(update_script)],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            print(f"  ✗ update_sensitivities.py failed: {result.stderr[:200]}")
            return False
        print("  ✓ Sensitivities updated")
        lines = result.stdout.strip().split('\n')
        for line in lines[-5:]:
            print(f"    {line}")
    else:
        print(f"  ⚠ {update_script} not found, skipping")

    print(f"\n✅ Refresh complete at: {datetime.now().isoformat()}")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
