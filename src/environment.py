import os
from typing import Optional

from dotenv import dotenv_values

from src.sheets import Sheet

PREFIX = "flextensions_"

DEFAULT_COURSE_NAME = "PLEASE SET A COURSE NAME"
DEFAULT_REPLY_TO_EMAIL = "PLEASE SET REPLY-TO EMAIL"

DEFAULT_AUTO_APPROVE_THRESHOLD = 1
DEFAULT_AUTO_APPROVE_THRESHOLD_DSP = 1
DEFAULT_APPROVE_ASSIGNMENT_THRESHOLD = 1
DEFAULT_MAX_TOTAL_REQUESTED_EXTENSIONS_THRESHOLD = 3

DEFAULT_EMAIL_FROM = "[{}] <{}@berkeley.edu>".format(DEFAULT_COURSE_NAME, DEFAULT_COURSE_NAME)
DEFAULT_EMAIL_SUBJECT = "[CS 000] Extension Request Update"
DEFAULT_EMAIL_SIGNATURE = "{} Staff".format(DEFAULT_COURSE_NAME)

DEFAULT_EXTEND_GRADESCOPE_ASSIGNMENTS = "No"
DEFAULT_EXTEND_PENSIEVE_ASSIGNMENTS = "No"

class Environment:
    @staticmethod
    def clear():
        keys = os.environ.keys()
        for key in keys:
            if key.startswith(PREFIX):
                del os.environ[key]

    @staticmethod
    def contains(key: str) -> bool:
        return os.getenv(PREFIX + key) is not None and str(os.getenv(PREFIX + key)).strip() != ""

    @staticmethod
    def _safe_get(key: str, default: str = None) -> Optional[str]:
        if os.getenv(PREFIX + key):
            data = str(os.getenv(PREFIX + key)).strip()
            if data:
                return data
        return default

    # @staticmethod
    # def get(key: str) -> Any:
    #     if not os.getenv(PREFIX + key):
    #         raise ConfigurationError("Environment variable not set: " + key)
    #     return os.getenv(PREFIX + key)

    @staticmethod
    def get_auto_approve_threshold() -> int:
        return int(Environment._safe_get("AUTO_APPROVE_THRESHOLD", DEFAULT_AUTO_APPROVE_THRESHOLD))

    @staticmethod
    def get_auto_approve_threshold_dsp() -> int:
        return int(Environment._safe_get("AUTO_APPROVE_THRESHOLD_DSP", DEFAULT_AUTO_APPROVE_THRESHOLD_DSP))

    @staticmethod
    def get_max_total_requested_extensions_threshold() -> int:
        return int(Environment._safe_get("MAX_TOTAL_REQUESTED_EXTENSIONS_THRESHOLD", DEFAULT_MAX_TOTAL_REQUESTED_EXTENSIONS_THRESHOLD))

    @staticmethod
    def get_auto_approve_assignment_threshold() -> int:
        return int(Environment._safe_get("AUTO_APPROVE_ASSIGNMENT_THRESHOLD", DEFAULT_APPROVE_ASSIGNMENT_THRESHOLD))

    @staticmethod
    def get_course_name() -> str:
        return Environment._safe_get("COURSE_NAME", DEFAULT_COURSE_NAME)

    @staticmethod
    def get_reply_to_email() -> str:
        return Environment._safe_get("REPLY_TO_EMAIL", DEFAULT_REPLY_TO_EMAIL)

    @staticmethod
    def get_email_from() -> str:
        return Environment._safe_get("EMAIL_FROM", DEFAULT_EMAIL_FROM)

    @staticmethod
    def get_email_subject() -> str:
        return Environment._safe_get("EMAIL_SUBJECT", DEFAULT_EMAIL_SUBJECT)

    @staticmethod
    def get_email_signature() -> str:
        return Environment._safe_get("EMAIL_SIGNATURE", DEFAULT_EMAIL_SIGNATURE)

    @staticmethod
    def get_email_cc() -> Optional[str]:
        return Environment._safe_get("EMAIL_CC")

    @staticmethod
    def get_slack_endpoint() -> Optional[str]:
        return Environment._safe_get("SLACK_ENDPOINT")

    @staticmethod
    def get_slack_debug_endpoint() -> Optional[str]:
        return Environment._safe_get("SLACK_DEBUG_ENDPOINT")

    @staticmethod
    def get_slack_tag_list() -> Optional[str]:
        return Environment._safe_get("SLACK_TAG_LIST")

    @staticmethod
    def get_extend_gradescope_assignments() -> bool:
        return Environment._safe_get("EXTEND_GRADESCOPE_ASSIGNMENTS", DEFAULT_EXTEND_GRADESCOPE_ASSIGNMENTS)

    @staticmethod
    def get_gradescope_email() -> Optional[str]:
        return Environment._safe_get("GRADESCOPE_EMAIL")

    @staticmethod
    def get_gradescope_password() -> Optional[str]:
        return Environment._safe_get("GRADESCOPE_PASSWORD")

    @staticmethod
    def get_extend_pensieve_assignments() -> Optional[str]:
        return Environment._safe_get("EXTEND_PENSIEVE_ASSIGNMENTS", DEFAULT_EXTEND_PENSIEVE_ASSIGNMENTS)

    @staticmethod
    def get_pensieve_email() -> Optional[str]:
        return Environment._safe_get("PENSIEVE_EMAIL")

    @staticmethod
    def get_pensieve_api_token() -> Optional[str]:
        return Environment._safe_get("PENSIEVE_API_TOKEN")

    @staticmethod
    def get_spreadsheet_url() -> Optional[str]:
        return Environment._safe_get("SPREADSHEET_URL")

    @staticmethod
    def configure_env_vars(sheet: Sheet):
        """
        Reads environment variables from the "Environment Variables" sheet, and stores them into this process's
        environment variables for downstream use. Expects two columns: a "key" column, and a "value"
        """
        records = sheet.get_all_records()
        for record in records:
            key = record.get("key")
            value = record.get("value")
            if not key:
                continue
            os.environ[PREFIX + key] = str(value)

        # Load local environment variables now from .env, which override remote provided variables for debugging
        if os.path.exists(".env-pytest"):
            for key, value in dotenv_values(".env-pytest").items():
                if key == "APP_MASTER_SECRET":
                    os.environ[key] = value
                else:
                    os.environ[PREFIX + key] = value