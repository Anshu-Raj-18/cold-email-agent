import os
import base64
import logging
from pathlib import Path
from email.message import EmailMessage
from typing import Optional, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config import config

logger = logging.getLogger(__name__)

# Gmail API Scopes needed to send and compose drafts
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose"
]

class EmailService:
    """
    Handles Gmail API OAuth2 authentication, email drafting, and email sending.
    """

    def __init__(self):
        self.creds: Optional[Credentials] = None
        self.service = None

    def authenticate(self, credentials_path: Optional[Path] = None, token_path: Optional[Path] = None) -> bool:
        """
        Authenticates with Gmail API using OAuth2 flow.
        Returns True if authenticated successfully, False otherwise.
        """
        creds_path = credentials_path or config.gmail_credentials_file
        tok_path = token_path or config.gmail_token_file

        # Load existing token if available
        if tok_path.exists():
            try:
                self.creds = Credentials.from_authorized_user_file(str(tok_path), SCOPES)
            except Exception as e:
                logger.warning(f"Failed to load token file {tok_path}: {e}")
                self.creds = None

        # Refresh or authenticate via flow if invalid
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Could not refresh OAuth token: {e}")
                    self.creds = None

            if not self.creds:
                if not creds_path.exists():
                    logger.warning(f"Credentials file '{creds_path}' not found.")
                    return False

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    # Save refreshed token
                    with open(tok_path, "w") as token_file:
                        token_file.write(self.creds.to_json())
                    logger.info(f"OAuth token successfully saved to {tok_path}")
                except Exception as e:
                    logger.error(f"OAuth authentication flow failed: {e}")
                    return False

        try:
            self.service = build("gmail", "v1", credentials=self.creds)
            logger.info("Gmail API service successfully initialized.")
            return True
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
            return False

    def send_email(self, recipient_email: str, subject: str, body_text: str, attachments: Optional[list] = None) -> Dict[str, Any]:
        """
        Sends an email using Gmail API with optional file attachments.
        """
        if not self.service:
            raise RuntimeError("Gmail service is not authenticated. Call authenticate() first.")

        message = EmailMessage()
        message.set_content(body_text)
        message["To"] = recipient_email
        message["From"] = config.sender_email
        message["Subject"] = subject

        if attachments:
            for att_path in attachments:
                if att_path and os.path.exists(att_path):
                    try:
                        with open(att_path, "rb") as f:
                            file_data = f.read()
                            file_name = os.path.basename(att_path)
                        message.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)
                        logger.info(f"Attached file {file_name} to email for {recipient_email}")
                    except Exception as e:
                        logger.warning(f"Failed to attach file {att_path}: {e}")

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        try:
            sent_message = (
                self.service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            logger.info(f"Email sent successfully. Message ID: {sent_message.get('id')}")
            return {"status": "success", "id": sent_message.get("id")}
        except HttpError as error:
            logger.error(f"Gmail API HTTP Error while sending email: {error}")
            return {"status": "error", "error": str(error)}

    def create_draft(self, recipient_email: str, subject: str, body_text: str, attachments: Optional[list] = None) -> Dict[str, Any]:
        """
        Creates a draft in the user's Gmail account with optional attachments.
        """
        if not self.service:
            raise RuntimeError("Gmail service is not authenticated. Call authenticate() first.")

        message = EmailMessage()
        message.set_content(body_text)
        message["To"] = recipient_email
        message["From"] = config.sender_email
        message["Subject"] = subject

        if attachments:
            for att_path in attachments:
                if att_path and os.path.exists(att_path):
                    try:
                        with open(att_path, "rb") as f:
                            file_data = f.read()
                            file_name = os.path.basename(att_path)
                        message.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)
                    except Exception as e:
                        logger.warning(f"Failed to attach file {att_path}: {e}")

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"message": {"raw": encoded_message}}

        try:
            draft = (
                self.service.users()
                .drafts()
                .create(userId="me", body=create_message)
                .execute()
            )
            logger.info(f"Draft created successfully. Draft ID: {draft.get('id')}")
            return {"status": "success", "id": draft.get("id")}
        except HttpError as error:
            logger.error(f"Gmail API HTTP Error while creating draft: {error}")
            return {"status": "error", "error": str(error)}

