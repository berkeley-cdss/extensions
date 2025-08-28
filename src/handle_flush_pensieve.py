from src.assignments import AssignmentList
from src.environment import Environment
from src.errors import ConfigurationError
from src.pensieve import Pensieve
from src.record import StudentRecord
from src.sheets import (SHEET_ASSIGNMENTS, SHEET_ENVIRONMENT_VARIABLES,
                        SHEET_STUDENT_RECORDS, BaseSpreadsheet)
from src.slack import SlackManager


def handle_flush_pensieve(request_json):
    if "spreadsheet_url" not in request_json:
        raise ConfigurationError("handle_flush_pensieve expects spreadsheet_url parameter")

    # Get pointers to sheets.
    base = BaseSpreadsheet(spreadsheet_url=request_json["spreadsheet_url"])
    sheet_assignments = base.get_sheet(SHEET_ASSIGNMENTS)
    sheet_records = base.get_sheet(SHEET_STUDENT_RECORDS)
    sheet_env_vars = base.get_sheet(SHEET_ENVIRONMENT_VARIABLES)

    # Set up environment variables.
    Environment.configure_env_vars(sheet_env_vars)

    # Fetch assignments.
    assignments = AssignmentList(sheet=sheet_assignments)

    # Fetch records.
    records = sheet_records.get_all_records()

    slack = SlackManager()

    pensieve = Pensieve()

    all_warnings = []
    successes = []
    failures = []
    for i, table_record in enumerate(records):
        student = StudentRecord(table_index=i, table_record=table_record, sheet=sheet_records)
        if student.should_flush_pensieve():
            w = student.apply_extensions_pensieve(assignments=assignments, pensieve=pensieve)
            if len(w) > 0:
                failures.append(student.get_email())
                all_warnings.extend(w)
            else:
                successes.append(student.get_email())
                student.set_flush_pensieve_status_success()

        student.flush()

    for warning in all_warnings:
        slack.add_warning(warning)

    summary = "Flush Pensieve Summary:" + "\n"
    if len(successes) > 0:
        summary += "\n" + "*Successes:* " + ", ".join(successes)
    if len(failures) > 0:
        summary += "\n" + "*Failures:* " + ", ".join(failures)
    if len(successes) + len(failures) == 0:
        summary += (
            "\n"
            + "No student records processed. To process a student record, create a `flush_pensieve` column on the Roster sheet, and set the value to TRUE for each record you would like to flush to Pensieve."
        )

    slack.send_message(summary)