import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email via SES. Never raises - logs and returns
    False on failure, so callers like forgot-password keep working."""
    sender = os.getenv("SES_SENDER_EMAIL")
    region = os.getenv("AWS_REGION")

    if not sender or not region:
        logger.error("SES_SENDER_EMAIL or AWS_REGION is not configured")
        return False

    client = boto3.client("ses", region_name=region)

    try:
        client.send_email(
            Source=sender,
            Destination={"ToAddresses": [to]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )
        return True
    except (BotoCoreError, ClientError):
        logger.exception("Failed to send email to %s", to)
        return False
