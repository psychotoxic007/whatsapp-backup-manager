"""Cloud Manager for Google Drive integration."""

import os
import logging
import pickle
import sys
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core.exceptions import GoogleAPIError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging with UTF-8 encoding for Windows compatibility
logger = logging.getLogger(__name__)

# Only configure if not already configured by parent
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    # Force UTF-8 encoding for Windows
    if hasattr(handler.stream, 'reconfigure'):
        handler.stream.reconfigure(encoding='utf-8')
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class CloudManager:
    """Manages Google Drive interactions for WhatsApp backup files."""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.pickle'
    
    # Patterns to search for WhatsApp backup files
    BACKUP_PATTERNS = ['msgstore', '.db', '.tar', 'backup', 'whatsapp']
    
    def __init__(self, credentials_path: str = None):
        """Initialize CloudManager with Google Drive API.
        
        Args:
            credentials_path: Path to credentials.json file. 
                            Defaults to project root.
        """
        self.credentials_path = credentials_path or self.CREDENTIALS_FILE
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google Drive API using credentials.json.
        
        Handles both service account and OAuth2 flows.
        Generates and caches token.pickle for subsequent runs.
        """
        try:
            creds = None
            
            # Try to load cached token first
            if os.path.exists(self.TOKEN_FILE):
                try:
                    with open(self.TOKEN_FILE, 'rb') as token:
                        creds = pickle.load(token)
                    logger.info("[OK] Loaded cached token from token.pickle")
                except Exception as e:
                    logger.warning(f"Failed to load cached token: {e}. Re-authenticating...")
                    creds = None
            
            # If no valid cached token, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("[*] Token expired. Refreshing...")
                    creds.refresh(Request())
                else:
                    # Use InstalledAppFlow for OAuth2
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(
                            f"credentials.json not found at {self.credentials_path}. "
                            f"Please download it from Google Cloud Console."
                        )
                    
                    logger.info(f"[*] Authenticating with {self.credentials_path}...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    logger.info("[OK] Authentication successful")
                
                # Save token for future use
                with open(self.TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
                logger.info("[OK] Token saved to token.pickle for future use")
            
            # Build the Drive API service
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("[OK] Google Drive API service initialized")
            
        except FileNotFoundError as e:
            logger.error(f"[ERROR] File not found: {e}")
            raise
        except GoogleAuthError as e:
            logger.error(f"[ERROR] Google authentication error: {e}")
            raise
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error during authentication: {e}")
            raise
    
    def list_backups(self, max_results: int = 50) -> List[Dict]:
        """Search Google Drive for WhatsApp backup files.
        
        Args:
            max_results: Maximum number of files to return (default: 50)
        
        Returns:
            List of dictionaries containing file metadata
        
        Raises:
            GoogleAPIError: If Drive API call fails
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call _authenticate() first.")
        
        try:
            backups = []
            
            # Build search query for backup file patterns
            query_parts = []
            for pattern in self.BACKUP_PATTERNS:
                query_parts.append(f"name contains '{pattern}'")
            
            query = " or ".join(query_parts)
            query += " and trashed = false"  # Exclude deleted files
            
            logger.info("[*] Searching Google Drive for backup files...")
            logger.debug(f"Search query: {query}")
            
            # Execute search with pagination
            request = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, size, createdTime, modifiedTime, webViewLink, mimeType)',
                pageSize=max_results,
                orderBy='modifiedTime desc'  # Most recent first
            )
            
            results = request.execute()
            files = results.get('files', [])
            
            if not files:
                logger.info("[*] No backup files found on Google Drive.")
                return []
            
            # Parse results
            for file in files:
                backup_info = {
                    'id': file.get('id'),
                    'name': file.get('name'),
                    'size': file.get('size', 'unknown'),
                    'created_time': file.get('createdTime'),
                    'modified_time': file.get('modifiedTime'),
                    'web_view_link': file.get('webViewLink'),
                    'mime_type': file.get('mimeType')
                }
                backups.append(backup_info)
            
            logger.info(f"[OK] Found {len(backups)} backup file(s)")
            return backups
            
        except HttpError as e:
            logger.error(f"[ERROR] Google Drive API error: {e}")
            raise
        except GoogleAPIError as e:
            logger.error(f"[ERROR] Google API error: {e}")
            raise
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error while listing backups: {e}")
            raise
    
    def download_backup(self, file_id: str, output_path: str) -> bool:
        """Download a backup file from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            output_path: Local path to save the file
        
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call _authenticate() first.")
        
        try:
            logger.info(f"[*] Downloading backup file {file_id}...")
            
            request = self.service.files().get_media(fileId=file_id)
            
            with open(output_path, 'wb') as f:
                from googleapiclient.http import MediaIoBaseDownload
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            logger.info(f"[OK] File downloaded to {output_path}")
            return True
            
        except HttpError as e:
            logger.error(f"[ERROR] Failed to download file: {e}")
            return False
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error during download: {e}")
            return False
    
    def get_backup_info(self, file_id: str) -> Optional[Dict]:
        """Get detailed information about a specific backup file.
        
        Args:
            file_id: Google Drive file ID
        
        Returns:
            Dictionary with file metadata or None if not found
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call _authenticate() first.")
        
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, size, createdTime, modifiedTime, webViewLink, mimeType, owners'
            ).execute()
            
            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'size': file.get('size'),
                'created_time': file.get('createdTime'),
                'modified_time': file.get('modifiedTime'),
                'web_view_link': file.get('webViewLink'),
                'mime_type': file.get('mimeType'),
                'owners': file.get('owners')
            }
            
        except HttpError as e:
            logger.error(f"[ERROR] Failed to get file info: {e}")
            return None
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error: {e}")
            return None
