import sys
import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose"
]

def main():
    creds_path = Path("credentials.json")
    token_path = Path("token.json")
    
    if not creds_path.exists():
        print("Error: credentials.json not found!", flush=True)
        return

    print("=" * 70, flush=True)
    print(" GMAIL API OAUTH AUTHENTICATION SETUP", flush=True)
    print("=" * 70, flush=True)
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(creds_path),
            scopes=SCOPES
        )
        
        # run_local_server generates and handles PKCE code verifier cleanly
        creds = flow.run_local_server(
            host="localhost",
            port=8080,
            authorization_prompt_message="\nPlease visit this URL to authorize: {url}\n",
            open_browser=True
        )
        
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

        print("\n[SUCCESS] OAuth token successfully saved to 'token.json'!", flush=True)
        
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        print(f"[SUCCESS] Authenticated Gmail Account: {profile.get('emailAddress')}", flush=True)
        print("=" * 70, flush=True)
    except Exception as e:
        print(f"\n[ERROR] Authentication failed: {e}", flush=True)

if __name__ == "__main__":
    main()
