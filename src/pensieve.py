from typing import List

import requests

from src.environment import Environment
from src.errors import KnownError
from src.utils import truncate


class Pensieve:
    """
    Pensieve client to apply extensions for a student on an assignment.
    """

    def __init__(self) -> None:
        email = Environment.get_pensieve_email()
        token = Environment.get_pensieve_api_token()

        if not email:
            raise KnownError("PENSIEVE_EMAIL must be set to use Pensieve.")
        if not token:
            raise KnownError("PENSIEVE_API_TOKEN must be set to use Pensieve.")

        self.base_url = "https://api.pensieve.co"
        self.email = email
        self.token = token

    @staticmethod
    def is_enabled():
        return Environment.get_extend_pensieve_assignments() in ["Yes", "TRUE"]

    def apply_extension(self, assignment_name: str, assignment_urls: List[str], email: str, num_days: int) -> List[str]:
        warnings = []
        course_name = Environment.get_course_name()

        for assignment_url in assignment_urls:
            prefix = '[{}] [{}{}] [{}] [{}] '.format(
                email, course_name + ' ', assignment_name, assignment_url, num_days)
            try:
                resp = requests.post(
                    f"{self.base_url}/api/b2s/v1/external-client/grant-extension",
                    headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
                    json={
                        "assignment_url": assignment_url,
                        "student_email": email,
                        "num_days": num_days,
                    },
                    timeout=30,
                )
                if resp.status_code != 200:
                    raise Exception(f"HTTP {resp.status_code}: {truncate(resp.text)}")
                data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                if not data or not data.get("success", False):
                    raise Exception(truncate(data))
            except Exception as err:
                warnings.append(
                    prefix
                    + f"failed to extend assignment in Pensieve: internal Pensieve error occurred ({truncate(err)})"
                )
        return warnings
