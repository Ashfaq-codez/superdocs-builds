import httpx
import time

API_URL = "http://localhost:8000/compositions"

def run_demo():
    print("\n" + "="*50)
    print(" HR COMPOSER - REAL ARTIFACT RUNTIME DEMO")
    print("="*50 + "\n")

    hr_data = {
        "hr_record": {
            "candidate_name": "John Smith",
            "role": "Software Engineer",
            "salary": "$120,000",
            "location": "San Francisco, CA",
            "employment_type": "Full-time",
            "start_date": "September 15, 2026",
            "benefits": "Comprehensive health, dental, vision, and 401(k) matching." # <--- ADD THIS
        }
    }

    with httpx.Client() as client:
        # 1. Compose Document
        print("1. Submitting HR Record (California)...")
        res = client.post(API_URL, json=hr_data)
        res.raise_for_status()
        comp_id = res.json()["composition_id"]
        status = res.json()["status"]
        
        print(f"   [+] Composition Created: {comp_id}")
        print(f"   [!] Status halted at: {status}\n")

        # 2. Human Approval Gate
        input(">>> PRESS ENTER TO SIMULATE HUMAN APPROVAL <<<")
        print("\n2. Approving Document Edit Proposal...")
        res = client.post(f"{API_URL}/{comp_id}/approve")
        res.raise_for_status()
        print(f"   [+] Status updated to: {res.json()['status']}\n")

        # 3. Export Artifacts
        print("3. Exporting to DOCX and PDF...")
        res = client.post(f"{API_URL}/{comp_id}/export", json={"formats": ["DOCX", "PDF"]})
        res.raise_for_status()
        artifacts = res.json()["artifacts"]
        
        print(f"   [+] Status updated to: {res.json()['status']}")
        print("\n" + "="*50)
        print(" ARTIFACTS GENERATED SUCCESSFULLY")
        print("="*50)
        
        for a in artifacts:
            # We construct the download URL using the safe reference returned by the SDK
            filename = a['reference'].split('/')[-1]
            download_url = f"{API_URL}/{comp_id}/artifacts/{filename}"
            print(f" - {a['format']} Download Link: {download_url}")
            
        print("\n(You can Ctrl+Click the links above in your terminal to open them!)\n")

if __name__ == "__main__":
    run_demo()