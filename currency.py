def convert_currency(
    amount,
    from_currency,
    to_currency,
    rate
):

    if from_currency == to_currency:
        return amount

    return amount * rate
def get_exchange_rate(
    exchange_rates,
    date,
    from_currency,
    to_currency
):

    result = exchange_rates[
        (exchange_rates["rate_date"] == date)
        &
        (exchange_rates["from_currency"] == from_currency)
        &
        (exchange_rates["to_currency"] == to_currency)
    ]

    if result.empty:
        return None

    return result.iloc[0]["rate"]
def classify_events(user_events):

    recurring = user_events[
        user_events["is_recurring"] == True
    ]

    one_time = user_events[
        user_events["is_recurring"] != True
    ]

    return recurring, one_time