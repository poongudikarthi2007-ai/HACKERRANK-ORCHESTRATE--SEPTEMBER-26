import pandas as pd


def create_full_payment_plan(
    request_date,
    requested_amount
):
    return {
        "type": "full_payment",
        "amount": float(requested_amount),
        "payment_date": pd.Timestamp(
            request_date
        ).strftime("%Y-%m-%d")
    }


def create_partial_payment_plan(
    request_date,
    amount_safe,
    requested_amount,
    earliest_date
):
    remaining_amount = (
        float(requested_amount)
        - float(amount_safe)
    )

    return {
        "type": "partial_payment",
        "initial_payment": float(amount_safe),
        "remaining_amount": remaining_amount,
        "payment_start_date": pd.Timestamp(
            request_date
        ).strftime("%Y-%m-%d"),
        "full_payment_date": pd.Timestamp(
            earliest_date
        ).strftime("%Y-%m-%d")
    }