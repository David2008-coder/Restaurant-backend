"""Thin wrapper around Paystack's REST API. Kept isolated so the payment
provider can be swapped without touching views/serializers."""
import requests
from django.conf import settings

BASE_URL = "https://api.paystack.co"


def _headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def initialize_transaction(email: str, amount_naira, reference: str, callback_url: str = ""):
    """amount_naira is converted to kobo, as Paystack requires the smallest currency unit."""
    payload = {
        "email": email,
        "amount": int(float(amount_naira) * 100),
        "reference": reference,
        "callback_url": callback_url,
    }
    resp = requests.post(f"{BASE_URL}/transaction/initialize", json=payload, headers=_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()


def verify_transaction(reference: str):
    resp = requests.get(f"{BASE_URL}/transaction/verify/{reference}", headers=_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()
