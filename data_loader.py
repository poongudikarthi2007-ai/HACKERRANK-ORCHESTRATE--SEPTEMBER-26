from pathlib import Path

import pandas as pd


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "dataset"


# =========================================================
# LOAD ALL DATA
# =========================================================

def load_data():

    requests = pd.read_csv(
        DATASET_PATH / "requests.csv"
    )

    sample_requests = pd.read_csv(
        DATASET_PATH / "sample_requests.csv"
    )

    financial_profiles = pd.read_csv(
        DATASET_PATH / "financial_profiles.csv"
    )

    financial_events = pd.read_csv(
        DATASET_PATH / "financial_events.csv"
    )

    exchange_rates = pd.read_csv(
        DATASET_PATH / "exchange_rates.csv"
    )

    request_payment_options = pd.read_csv(
        DATASET_PATH / "request_payment_options.csv"
    )

    messages = pd.read_csv(
        DATASET_PATH / "messages.csv"
    )

    images = pd.read_csv(
        DATASET_PATH / "images.csv"
    )

    return (
        requests,
        sample_requests,
        financial_profiles,
        financial_events,
        exchange_rates,
        request_payment_options,
        messages,
        images
    )