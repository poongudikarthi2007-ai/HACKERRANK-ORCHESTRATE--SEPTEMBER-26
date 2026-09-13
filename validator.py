import pandas as pd


def validate_output(output, requests):

    errors = []

    required_columns = [
        "request_id",
        "amount_safe_to_pay",
        "affordability_status",
        "recommended_payment_method",
        "payment_plan",
        "earliest_date_for_full_payment",
        "spending_changes_needed",
        "decision_explanation"
    ]

    for column in required_columns:
        if column not in output.columns:
            errors.append(
                f"Missing column: {column}"
            )

    if "request_id" in output.columns:
        request_ids = set(
            requests["request_id"]
        )

        output_ids = set(
            output["request_id"]
        )

        invalid_ids = output_ids - request_ids

        if invalid_ids:
            errors.append(
                f"Invalid request IDs: {invalid_ids}"
            )

    return errors