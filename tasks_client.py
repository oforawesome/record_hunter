"""
tasks_client.py — Google Tasks API helper for Record Hunter.

Handles authentication and adding items to a Google Tasks list.
Reads credentials from Streamlit secrets (or .env locally).
"""

import json
import streamlit as st
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/tasks"]
TASKLIST_NAME = "Records to Hunt"


def get_tasks_service():
    """Build and return an authenticated Google Tasks service."""
    try:
        token_json = st.secrets["GOOGLE_TOKEN"]
    except KeyError:
        st.error("GOOGLE_TOKEN not found in Streamlit secrets.")
        return None

    creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)

    # Refresh token if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build("tasks", "v1", credentials=creds)


def get_or_create_tasklist(service):
    """Find the 'Records to Hunt' task list, or create it if it doesn't exist."""
    result = service.tasklists().list().execute()
    for tl in result.get("items", []):
        if tl["title"] == TASKLIST_NAME:
            return tl["id"]

    # Create it if not found
    new_list = service.tasklists().insert(body={"title": TASKLIST_NAME}).execute()
    return new_list["id"]


def add_record_to_tasks(album_text):
    """
    Add a record to the 'Records to Hunt' Google Tasks list.
    album_text: e.g. "The Cure - Disintegration (1989)"
    Returns True on success, False on failure.
    """
    try:
        service = get_tasks_service()
        if not service:
            return False

        tasklist_id = get_or_create_tasklist(service)

        task = {"title": album_text}
        service.tasks().insert(tasklist=tasklist_id, body=task).execute()
        return True

    except Exception as e:
        st.error(f"Google Tasks error: {e}")
        return False
