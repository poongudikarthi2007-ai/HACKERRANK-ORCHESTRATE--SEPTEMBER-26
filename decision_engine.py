def choose_payment_method(
    amount_safe,
    requested_amount,
    earliest_date,
    request_date,
    allows_partial_payment,
    accepts_full,
    accepts_partial,
    accepts_installments
):

    # Full payment today
    if (
        amount_safe >= requested_amount
        and accepts_full
    ):
        return "full_payment"

    # Partial payment
    if (
        amount_safe > 0
        and amount_safe < requested_amount
        and allows_partial_payment
        and accepts_partial
        and earliest_date is not None
    ):
        return "partial_payment"

    # Wait
    if (
        earliest_date is not None
        and accepts_full
    ):
        return "wait"

    # Installments
    if accepts_installments:
        return "installments"

    return "not_recommended"
def determine_status(
    requested_amount,
    amount_safe,
    payment_method,
    earliest_date,
    request_date
):

    if (
        amount_safe >= requested_amount
        and payment_method == "full_payment"
    ):
        return "affordable_now"

    if payment_method in [
        "partial_payment",
        "installments"
    ]:
        return "affordable_with_plan"

    if (
        payment_method == "wait"
        and earliest_date is not None
    ):
        return "affordable_later"

    return "not_affordable"
def create_partial_payment_plan(
    request_date,
    amount_safe,
    requested_amount,
    earliest_date
):

    remaining = (
        requested_amount
        - amount_safe
    )

    return (
        f"{request_date.strftime('%Y-%m-%d')}:"
        f"{amount_safe}|"
        f"{earliest_date.strftime('%Y-%m-%d')}:"
        f"{remaining}"
    )
def create_full_payment_plan(
    request_date,
    amount
):

    return (
        f"{request_date.strftime('%Y-%m-%d')}:"
        f"{amount}"
    )
def no_payment_plan():

    return "none"
def create_spending_change(
    event_id,
    change_type,
    new_amount=None
):

    if change_type == "stop":
        return f"stop:{event_id}"

    if change_type == "reduce_to":
        return (
            f"reduce_to:{event_id}:"
            f"{new_amount}"
        )

    return "none"
def get_request_messages(
    request_id,
    messages
):

    result = messages[
        messages["request_id"]
        == request_id
    ]

    return result