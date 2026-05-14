from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import os
import requests
import time
from virustotal_python import Virustotal

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock databases (same as before)
SHA256_PACKS = [
    "hard_signatures/SHA256-Hashes_pack1.txt",
    "hard_signatures/SHA256-Hashes_pack2.txt",
    "hard_signatures/SHA256-Hashes_pack3.txt"
]

@app.post("/scan")
async def scan_file(file: UploadFile = File(...), vt_key: str = Form(None), md_key: str = Form(None)):
    contents = await file.read()
    file_hash = hashlib.sha256(contents).hexdigest()
    
    results = {
        "filename": file.filename,
        "hash": file_hash,
        "size": f"{len(contents) / 1024:.2f} KB",
        "virus_found": False,
        "vt_detections": "0 / 0",
        "md_detections": "0 / 0",
        "logs": []
    }
    
    results["logs"].append(f"[*] Analyzing target: {file.filename}")
    results["logs"].append(f"[*] SHA256 Fingerprint: {file_hash}")
    
    # Local check
    results["logs"].append("[*] Checking local threat database...")
    for pack in SHA256_PACKS:
        if os.path.exists(pack):
            with open(pack, 'r') as f:
                for line in f:
                    if file_hash == line.split(";")[0].strip():
                        results["virus_found"] = True
                        break
        if results["virus_found"]: break
    
    if results["virus_found"]:
        results["logs"].append("[!] THREAT DETECTED in local database!")
    else:
        results["logs"].append("[+] Local database check: SECURE")

    # VirusTotal
    if vt_key:
        results["logs"].append("[*] Querying VirusTotal Cloud...")
        try:
            # We don't upload the file in this simple version, just check hash report
            headers = {"x-apikey": vt_key}
            resp = requests.get(f"https://www.virustotal.com/api/v3/files/{file_hash}", headers=headers).json()
            if "data" in resp:
                stats = resp["data"]["attributes"]["last_analysis_stats"]
                results["vt_detections"] = f"{stats['malicious']} / {stats['malicious'] + stats['undetected']}"
                results["logs"].append(f"[!] VirusTotal: {stats['malicious']} engines flagged this.")
        except:
            results["logs"].append("[!] VirusTotal API error.")

    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
