# core/utils/email.py

import requests # we use it to call Brevo’s API, This library is used to send HTTP requests

import logging # Used to log errors if email fails.
from django.conf import settings

logger = logging.getLogger(__name__)

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def send_brevo_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Sends transactional email using Brevo API
    Used for:
    Email verification
    Password reset
    HR invite 
    update status 
    """

    payload = {
        "sender": {
            "email": settings.BREVO_SENDER_EMAIL,
            "name": settings.BREVO_SENDER_NAME,
        },
        "to": [
            {"email": to_email}      
        ],
        "subject": subject,
        "htmlContent": html_content,
    }

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY, # api-key → secret key from Brevo account. Without this, Brevo will reject request.
        "content-type": "application/json",
    }

    try: 
        response = requests.post(
            BREVO_URL, 
            json = payload, # json = payload → sends email data
            headers = headers, # headers=headers → sends API key
            timeout = 10, #  IMPORTANT: prevents hanging
        )   

        if response.status_code in (200, 201, 202):   
            return True   

        logger.error(f"Brevo error {response.status_code}: {response.text}")
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Brevo request failed: {e}")
        return False
