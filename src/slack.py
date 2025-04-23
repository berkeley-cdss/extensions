from typing import List
import logging 

from slack_sdk.webhook import WebhookClient, WebhookResponse
from tabulate import tabulate

from src.assignments import AssignmentList
from src.errors import SlackError
from src.record import StudentRecord
from src.submission import FormSubmission
from src.utils import Environment, cast_list_str


class SlackManager:
    """
    A container to hold Slack-related utilities.
    """

    def __init__(self) -> None:
        self.webhooks: List[WebhookClient] = []
        self.warnings = []
        self.silent = False

        webhook = Environment.get_slack_endpoint()
        debug_webhook = Environment.get_slack_debug_endpoint()
        
        if webhook:
            self.webhooks.append(WebhookClient(webhook))
        if debug_webhook and debug_webhook != webhook:
            self.webhooks.append(WebhookClient(debug_webhook))

        # after Slack configuration if there is no webhook then suppress any Slack action
        if not self.webhooks:
            # TODO: send warning that no slack endpoint is set up, printing log to GCP instead
            logging.warning("Failed to set up Slack as no webhook is provided.")
            self.silent = True

    def suppress(self):
        self.silent = True

    def add_warning(self, warning: str):
        if warning not in self.warnings:
            self.warnings.append(warning)

    def _get_submission_details_knows_assignments(self):
        text = "> *Email*: " + self.submission.get_email() + "\n"
        text += "> *Assignment(s)*: " + self.submission.get_raw_requests() + "\n"
        text += "> *Reason*: " + self.submission.get_reason().replace("\n", " ") + "\n"
        if self.submission.claims_dsp():
            text += "> *DSP Accomodations for Extensions*: " + self.submission.dsp_status() + "\n"
        if self.submission.has_partner():
            text += "> *Partner Email(s)*: " + ", ".join(self.submission.get_partner_emails()) + "\n"
        text += "> *Documentation*: " + self.submission.get_documentation() + "\n"
        return text

    def _get_submission_details_unknown_assignments(self):
        text = "> *Email*: " + self.submission.get_email() + "\n"
        text += "> *Notes*: " + self.submission.get_game_plan() + "\n"
        return text

    def set_current_student(self, submission: FormSubmission, student: StudentRecord, assignments: AssignmentList):
        self.submission = submission
        self.student = student
        self.assignments = assignments

    def get_warnings(self) -> str:
        warnings = ""
        warnings += "\n"
        warnings += "*Warnings:*\n"
        warnings += "```" + "\n"
        for w in self.warnings:
            warnings += w + "\n"
        warnings += "```"
        return warnings

    def send_message(self, message: str) -> None:
        if self.silent:
            # TODO: configure gcp log instead
            print("\n" + ("#" * 30) + "\n" + message.strip() + "\n" + "#" * 30)
            return

        if len(self.warnings) > 0:
            message += self.get_warnings()

        for webhook in self.webhooks:
            response = webhook.send(text=message)
            self.check_error(response)

    @staticmethod
    def get_tags() -> str:
        slack_tags = Environment.get_slack_tag_list()
        prefix = ""
        if slack_tags:
            uids = cast_list_str(slack_tags)
            prefix = " ".join([f"<@{uid}>" for uid in uids]) + " "
        return prefix

    def send_student_update(self, message: str, autoapprove: bool = False) -> None:
        message += "\n"
        if self.submission.knows_assignments():
            message += self._get_submission_details_knows_assignments()
        else:
            message += self._get_submission_details_unknown_assignments()

        message += "\n"
        rows = []
        for assignment in self.assignments:
            num_days = self.student.get_request(assignment.get_id())
            if num_days:
                rows.append([assignment.get_name(), num_days])
        if len(rows) > 0:
            message += "```"
            message += tabulate(rows)
            message += "```"
        message += "\n"
        message += "\n"

        if len(self.warnings) > 0:
            message += self.get_warnings()

        if self.silent:
            # TODO: configure gcp log instead
            print("\n" + ("#" * 30) + "\n" + message.strip() + "\n" + "#" * 30)
            return

        if autoapprove:
            for webhook in self.webhooks:
                response = webhook.send(text=message)
                self.check_error(response=response)
        else:
            # This isn't an auto-approval, so attach tags!
            tags = SlackManager.get_tags()
            message = tags + message
            for webhook in self.webhooks:
                response = webhook.send(
                    blocks=[
                        {"type": "section", "text": {"type": "mrkdwn", "text": message}},
                        {
                            "type": "actions",
                            "block_id": "approve_extension",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "View Spreadsheet"},
                                    "url": Environment.get_spreadsheet_url(),
                                },
                            ],
                        },
                    ]
                )
                self.check_error(response)

    def send_error(self, error: str) -> None:
        for webhook in self.webhooks:
            tags = SlackManager.get_tags()
            response = webhook.send(text=tags + "An error occurred: " + "\n" + "```" + "\n" + error + "\n" + "```")
            self.check_error(response=response)

    def check_error(self, response: WebhookResponse):
        if response.status_code != 200:
            raise SlackError(f"Status code not 200: {vars(response)}")
