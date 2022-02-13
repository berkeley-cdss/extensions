from datetime import datetime
from typing import List, Optional

import pytz
from gradescope_api.client import GradescopeClient
from gradescope_api.errors import GradescopeAPIError

from src.errors import GradescopeError, KnownError
from src.utils import Environment, cast_bool


class Gradescope:
    """
    An interface to apply extensions to Gradescope. This relies on `cs161-staff/gradescope-api`, an unofficial,
    minimal Gradescope API wrapper designed specifically for extension management.
    """

    def __init__(self) -> None:
        email = Environment.get("GRADESCOPE_EMAIL")
        password = Environment.get("GRADESCOPE_PASSWORD")

        try:
            self.client = GradescopeClient(email=email, password=password)
        except Exception as err:
            raise GradescopeError(f"Failed to sign into Gradescope: {err}")

    @staticmethod
    def is_enabled():
        return cast_bool(Environment.safe_get("EXTEND_GRADESCOPE_ASSIGNMENTS", "No"))

    def apply_extension(
        self,
        assignment_urls: List[str],
        email: str,
        new_due_date: datetime,
        new_hard_due_date: Optional[datetime] = None,
    ) -> List[str]:
        warnings = []
        for assignment_url in assignment_urls:
            try:
                course = self.client.get_course(course_url=assignment_url)
                student = course.get_student(email=email)
                if not student:
                    warnings.append(f"Student {email} not found on Gradescope course roster; check email!")
                    return warnings
                assignment = course.get_assignment(assignment_url=assignment_url)
                new_due_date_utc = new_due_date.astimezone(pytz.utc)
                new_hard_due_date_utc = new_hard_due_date.astimezone(pytz.utc) if new_hard_due_date else None
                if new_hard_due_date_utc and new_hard_due_date_utc < new_due_date_utc:
                    warnings.append(
                        f"New due date was after the designated hard due date, so extended assignment to the designated hard due date instead (email: {email}, assignment: {assignment_url})"
                    )
                    new_due_date = new_hard_due_date
                assignment.create_extension(
                    user_id=student.get_user_id(), due_date=new_due_date_utc, hard_due_date=new_hard_due_date_utc
                )
                print(f"Successfully extended deadline for {email} to {new_due_date} on assignment {assignment_url}")
            except Exception as err:
                print("GradescopeAPIError: " + str(err))
                warnings.append(
                    f"Could not extend assignment deadline for {email} for {assignment_url} (internal Gradescope error: {err})"
                )
        return warnings
