"""IMAP client managing Gmail IMAP connection and IDLE notifications."""

import imaplib
import logging
import ssl

from app.config import get_settings

logger = logging.getLogger(__name__)


class GmailIMAPClient:
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        email_address: str | None = None,
        password: str | None = None,
        use_ssl: bool = True,
    ):
        settings = get_settings()
        self.host = host or settings.IMAP_SERVER
        self.port = port or settings.IMAP_PORT
        self.email_address = email_address or settings.GMAIL_ADDRESS
        self.password = password or settings.GMAIL_APP_PASSWORD
        self.use_ssl = use_ssl
        self.imap: imaplib.IMAP4_SSL | None = None
        self._is_connected = False
        self._current_mailbox: str | None = None

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def connect(self) -> None:
        """Establishes IMAP connection with TLS."""
        try:
            if self.use_ssl:
                context = ssl.create_default_context()
                self.imap = imaplib.IMAP4_SSL(self.host, self.port, ssl_context=context)
            else:
                self.imap = imaplib.IMAP4(self.host, self.port)
            self._is_connected = True
            logger.info(f"Connected to IMAP server {self.host}:{self.port}")
        except Exception as e:
            self._is_connected = False
            raise ConnectionError(
                f"Failed to connect to IMAP server {self.host}:{self.port}: {e}"
            )

    def _get_oauth2_access_token(self) -> str | None:
        """Fetches a fresh access token using the OAuth refresh token."""
        settings = get_settings()
        if not (
            settings.GOOGLE_CLIENT_ID
            and settings.GOOGLE_CLIENT_SECRET
            and settings.GOOGLE_REFRESH_TOKEN
        ):
            return None
        try:
            import httpx

            resp = httpx.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": settings.GOOGLE_REFRESH_TOKEN,
                    "grant_type": "refresh_token",
                },
                timeout=10.0,
            )
            if resp.status_code == 200:
                return resp.json().get("access_token")
        except Exception as e:
            logger.warning(f"Failed to refresh OAuth token: {e}")
        return None

    def authenticate(self) -> None:
        """Authenticates with Gmail using OAuth2 if available, otherwise App Password."""
        if not self.imap or not self._is_connected:
            raise ConnectionError("IMAP connection is not open.")
        if not self.email_address:
            raise ValueError("Gmail address must be provided.")

        # Try OAuth2 first if refresh token is available
        access_token = self._get_oauth2_access_token()
        if access_token:
            try:
                auth_string = f"user={self.email_address}\x01auth=Bearer {access_token}\x01\x01".encode()
                typ, data = self.imap.authenticate("XOAUTH2", lambda x: auth_string)
                if typ == "OK":
                    logger.info(f"Authenticated as {self.email_address} via OAuth2")
                    return
            except Exception as e:
                logger.warning(
                    f"OAuth2 authentication attempt failed: {e}. Falling back to App Password..."
                )

        # Fallback to App Password
        if not self.password:
            raise ValueError(
                "Neither valid OAuth credentials nor Gmail App Password provided."
            )

        try:
            typ, data = self.imap.login(
                self.email_address, self.password.replace(" ", "")
            )
            if typ != "OK":
                raise PermissionError(f"Authentication failed: {data}")
            logger.info(f"Authenticated as {self.email_address} via App Password")
        except Exception as e:
            self._is_connected = False
            raise PermissionError(f"IMAP login failed: {e}")

    def select_mailbox(self, mailbox: str = "INBOX") -> tuple[int, int]:
        """Selects a mailbox (e.g. INBOX) and returns (num_messages, recent_messages)."""
        if not self.imap or not self._is_connected:
            raise ConnectionError("IMAP connection is not open.")

        typ, data = self.imap.select(mailbox)
        if typ != "OK":
            raise ValueError(f"Failed to select mailbox {mailbox}: {data}")

        self._current_mailbox = mailbox
        num_messages = int(data[0]) if data and data[0] else 0
        return num_messages, 0

    def search_uids_greater_than(self, last_uid: int) -> list[int]:
        """Searches for message UIDs strictly greater than last_uid."""
        if not self.imap or not self._is_connected:
            raise ConnectionError("IMAP connection is not open.")

        search_criteria = f"UID {last_uid + 1}:*" if last_uid > 0 else "ALL"
        typ, data = self.imap.uid("SEARCH", None, search_criteria)
        if typ != "OK" or not data or not data[0]:
            return []

        raw_uids = data[0].split()
        uids = [int(u) for u in raw_uids if int(u) > last_uid]
        uids.sort()
        return uids

    def get_latest_uids(self, limit: int = 50) -> list[int]:
        """Retrieves the latest N UIDs in the selected mailbox."""
        if not self.imap or not self._is_connected:
            raise ConnectionError("IMAP connection is not open.")

        typ, data = self.imap.uid("SEARCH", None, "ALL")
        if typ != "OK" or not data or not data[0]:
            return []

        raw_uids = data[0].split()
        uids = [int(u) for u in raw_uids]
        uids.sort()
        return uids[-limit:] if len(uids) > limit else uids

    def fetch_rfc822(self, uid: int) -> bytes | None:
        """Fetches raw RFC822 bytes for a message UID."""
        if not self.imap or not self._is_connected:
            raise ConnectionError("IMAP connection is not open.")

        typ, data = self.imap.uid("FETCH", str(uid), "(BODY.PEEK[] RFC822.SIZE)")
        if typ != "OK" or not data:
            return None

        for item in data:
            if isinstance(item, tuple) and len(item) > 1:
                return item[1]
        return None

    def idle_wait(self, timeout_seconds: int = 1500) -> bool:
        """
        Enters IMAP IDLE if supported, or polls with socket timeout.
        Returns True if EXISTS event received, False if timed out.
        """
        if not self.imap or not self._is_connected:
            raise ConnectionError("IMAP connection is not open.")

        # Check if Python imaplib has native idle() (e.g. Python 3.14+)
        if hasattr(self.imap, "idle"):
            try:
                with self.imap.idle(duration=timeout_seconds) as idler:
                    for response in idler:
                        if getattr(response, "type", "") == "EXISTS":
                            return True
                return False
            except Exception as e:
                logger.debug(f"Native idle() error or timeout: {e}")
                return False

        # Fallback IDLE implementation for standard Python imaplib
        tag = (
            self.imap._new_tag().decode()
            if isinstance(self.imap._new_tag(), bytes)
            else str(self.imap._new_tag())
        )
        cmd = f"{tag} IDLE\r\n"
        self.imap.send(cmd.encode("utf-8"))

        initial_resp = self.imap.readline()
        if not initial_resp or not initial_resp.startswith(b"+"):
            return False

        has_new_mail = False
        sock = self.imap.sock
        if sock:
            sock.settimeout(timeout_seconds)

        try:
            while True:
                line = self.imap.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="replace")
                if "EXISTS" in decoded or "RECENT" in decoded:
                    has_new_mail = True
                    break
                if decoded.startswith(tag):
                    break
        except (TimeoutError, OSError):
            pass  # Idle duration reached without new mail
        except Exception as e:
            logger.debug(f"IDLE wait ended: {e}")
        finally:
            # Terminate IDLE state with DONE
            try:
                self.imap.send(b"DONE\r\n")
                self.imap.readline()
            except Exception:
                pass
            if sock:
                try:
                    sock.settimeout(None)
                except Exception:
                    pass

        return has_new_mail

    def close(self) -> None:
        """Closes mailbox and logs out."""
        if self.imap:
            try:
                if self._current_mailbox:
                    self.imap.close()
            except Exception:
                pass
            try:
                self.imap.logout()
            except Exception:
                pass
        self._is_connected = False
        self._current_mailbox = None
        logger.info("IMAP client closed.")
