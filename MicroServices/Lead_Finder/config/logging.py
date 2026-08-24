import logging
import sys

from colorama import Fore, Style
from colorama import init as colorama_init
from leadfinder.config.settings import get_settings

colorama_init(autoreset=True)

LOG_FORMAT = "[%(levelname)s] [%(name)s] %(message)s"

NOISY_LOGGERS = [
    "httpx",
    "httpcore",
    "urllib3",
    "asyncio",
    "playwright",
    "starlette",
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
]

AGENT_COLORS = {
    "PLANNER": Fore.CYAN,
    "SCRAPER": Fore.BLUE,
    "EXTRACTION": Fore.YELLOW,
    "VALIDATION": Fore.GREEN,
    "DIAGNOSIS": Fore.MAGENTA,
    "HEALING": Fore.LIGHTMAGENTA_EX,
    "GRAPH": Fore.LIGHTCYAN_EX,
    "LLM": Fore.LIGHTBLUE_EX,
    "CRAWLER": Fore.LIGHTBLUE_EX,
}


class AgentConsoleFormatter(logging.Formatter):
    """Clean single-line console formatter with colored agent tags and aligned metadata."""

    def format(self, record: logging.LogRecord) -> str:
        # Determine tag color
        name = record.name.upper()
        agent_name = name.split(".")[0].split("_")[0]
        color = AGENT_COLORS.get(name) or AGENT_COLORS.get(agent_name) or Fore.WHITE

        if record.levelno >= logging.ERROR:
            tag = (
                f"{Fore.RED}[ERROR]{Style.RESET_ALL}   [{color}{name}{Style.RESET_ALL}]"
            )
        elif record.levelno >= logging.WARNING:
            tag = f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} [{color}{name}{Style.RESET_ALL}]"
        else:
            tag = f"[{color}{name:<12}{Style.RESET_ALL}]"

        msg = record.getMessage()
        return f"{tag} {msg}"


_logging_configured: bool = False
_is_cli_mode: bool = False


def setup_logging(verbose: bool = False, is_cli: bool = False) -> None:
    """Configure root and component loggers with noise suppression and clean formatting."""
    global _logging_configured, _is_cli_mode
    if is_cli:
        _is_cli_mode = True

    settings = get_settings()
    log_level = (
        logging.DEBUG
        if verbose
        else getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Suppress noisy third-party loggers unless verbose
    third_party_level = logging.DEBUG if verbose else logging.WARNING
    for noisy in NOISY_LOGGERS:
        logging.getLogger(noisy).setLevel(third_party_level)

    effective_cli = is_cli or _is_cli_mode
    formatter = (
        AgentConsoleFormatter() if effective_cli else logging.Formatter(LOG_FORMAT)
    )

    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    else:
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger conforming to standard application formatting."""
    global _logging_configured, _is_cli_mode
    if not _logging_configured:
        setup_logging(is_cli=_is_cli_mode)
    return logging.getLogger(name)
