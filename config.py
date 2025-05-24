"""Configuration settings for the municipal data chatbot."""

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from utils.exceptions import ConfigurationError, DataLoadError
from utils.logging import get_logger, log_exception

# Setup logger
logger = get_logger(__name__)

# Load environment variables
try:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigurationError("OPENAI_API_KEY environment variable not found")
    os.environ["OPENAI_API_KEY"] = api_key
    logger.info("Environment variables loaded successfully")
except Exception as e:
    log_exception(logger, e, "loading environment variables")
    raise ConfigurationError("Failed to load environment variables") from e

# Time configuration
try:
    LOCAL_TZ = ZoneInfo("Europe/Prague")
    CURRENT_TIME = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M (%Z)")
    logger.debug(f"Time configuration set: {CURRENT_TIME}")
except Exception as e:
    log_exception(logger, e, "setting up time configuration")
    raise ConfigurationError("Failed to configure timezone") from e

# Application settings
APP_TITLE: str = "Horšovský Týn – Chatbot"
APP_ICON: str = "🗂️"
LOGO_PATH: str = "static/assets/logo.png"

# CSV file paths
CSV_FILES: list[str] = [
    "data/data-v2/official_boards_tyn.csv",  # Official noticeboard data
    "data/data-v2/messages_tyn.csv",  # News and notices
    "data/data-v2/editors_tyn.csv",  # Website content
]

# LLM settings
MODEL_NAME: str = "gpt-4o-mini"
TEMPERATURE: float = 0.0

# Eval results settings
EVAL_RESULTS_DIR: str = "data/eval-streamlit"
EVAL_RESULTS_FILE: str | None = "eval_grades_with_ground_truth_20250524_080149.json"  # Optional specific file, None = use latest


def validate_csv_files(csv_files: list[str], base_path: Path | None = None) -> list[Path]:
    """Validate that all CSV files exist and are readable.

    Args:
        csv_files: List of CSV file paths
        base_path: Base path to resolve relative paths

    Returns:
        List of validated Path objects

    Raises:
        DataLoadError: If any CSV file is missing or unreadable

    """
    validated_files = []

    for file_path in csv_files:
        try:
            if base_path:
                full_path = base_path / file_path
            else:
                full_path = Path(file_path)

            if not full_path.exists():
                raise DataLoadError(f"CSV file not found: {full_path}")

            if not full_path.is_file():
                raise DataLoadError(f"Path is not a file: {full_path}")

            if not full_path.suffix.lower() == ".csv":
                logger.warning(f"File does not have .csv extension: {full_path}")

            # Test if file is readable
            try:
                with open(full_path, encoding='utf-8') as f:
                    f.read(1)  # Try to read one character
            except Exception as e:
                raise DataLoadError(f"Cannot read CSV file {full_path}: {e}") from e

            validated_files.append(full_path)
            logger.debug(f"Validated CSV file: {full_path}")

        except Exception as e:
            log_exception(logger, e, f"validating CSV file {file_path}")
            if isinstance(e, DataLoadError):
                raise
            raise DataLoadError(f"Error validating CSV file {file_path}") from e

    logger.info(f"Successfully validated {len(validated_files)} CSV files")
    return validated_files


def validate_logo_file(logo_path: str) -> Path:
    """Validate that the logo file exists.

    Args:
        logo_path: Path to the logo file

    Returns:
        Validated Path object

    Raises:
        ConfigurationError: If logo file is missing

    """
    try:
        logo_file = Path(logo_path)
        if not logo_file.exists():
            raise ConfigurationError(f"Logo file not found: {logo_file}")

        logger.debug(f"Validated logo file: {logo_file}")
        return logo_file

    except Exception as e:
        log_exception(logger, e, f"validating logo file {logo_path}")
        if isinstance(e, ConfigurationError):
            raise
        raise ConfigurationError(f"Error validating logo file {logo_path}") from e


def get_system_prompt() -> str:
    """Get the system prompt with current timestamp from external file.

    Returns:
        Formatted system prompt string

    Raises:
        ConfigurationError: If prompt file cannot be loaded

    """
    try:
        prompt_file = Path(__file__).parent / "prompts" / "system_prompt.txt"

        if not prompt_file.exists():
            raise ConfigurationError(f"System prompt file not found: {prompt_file}")

        with open(prompt_file, encoding="utf-8") as f:
            prompt_template = f.read()

        if not prompt_template.strip():
            raise ConfigurationError("System prompt file is empty")

        # Update current time for prompt
        current_time = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M (%Z)")
        formatted_prompt = prompt_template.format(current_time=current_time)

        logger.debug("System prompt loaded and formatted successfully")
        return formatted_prompt

    except Exception as e:
        log_exception(logger, e, "loading system prompt")
        if isinstance(e, ConfigurationError):
            raise
        raise ConfigurationError("Failed to load system prompt") from e


def get_latest_eval_file(eval_dir: str = EVAL_RESULTS_DIR) -> Path | None:
    """Get the latest eval results file based on timestamp in filename.

    Args:
        eval_dir: Directory containing eval result files

    Returns:
        Path to latest eval file or None if no files found

    """
    try:
        eval_path = Path(eval_dir)
        if not eval_path.exists():
            logger.warning(f"Eval results directory not found: {eval_path}")
            return None

        # Find all JSON files in the directory
        json_files = list(eval_path.glob("*.json"))
        if not json_files:
            logger.warning(f"No JSON files found in eval directory: {eval_path}")
            return None

        # Sort by modification time (newest first)
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        logger.debug(f"Latest eval file found: {latest_file}")
        return latest_file

    except Exception as e:
        log_exception(logger, e, "finding latest eval file")
        return None


def get_eval_file_path() -> Path | None:
    """Get the eval file path based on configuration.

    Returns:
        Path to eval file or None if not found

    """
    try:
        if EVAL_RESULTS_FILE:
            # Use specific file if configured
            eval_path = Path(EVAL_RESULTS_DIR) / EVAL_RESULTS_FILE
            if eval_path.exists():
                logger.debug(f"Using configured eval file: {eval_path}")
                return eval_path
            else:
                logger.warning(f"Configured eval file not found: {eval_path}")
                return None
        else:
            # Use latest file
            return get_latest_eval_file()

    except Exception as e:
        log_exception(logger, e, "getting eval file path")
        return None


# Validate configuration on import only if running from the correct directory
try:
    # Only validate if we can find the CSV files from current directory
    # This prevents validation failures when importing from eval/ subdirectory
    if Path("data/data-v2").exists():
        validate_csv_files(CSV_FILES)
        validate_logo_file(LOGO_PATH)
        logger.info("Configuration validation completed successfully")
    else:
        logger.info("Skipping configuration validation - running from subdirectory")
except Exception as e:
    logger.error(f"Configuration validation failed: {e}")
    # Don't raise here to allow imports to succeed, but log the error
