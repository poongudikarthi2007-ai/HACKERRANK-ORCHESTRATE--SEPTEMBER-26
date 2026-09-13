import pandas as pd


# =========================================================
# CREATE 90-DAY FORECAST
# =========================================================

def create_forecast(
    request_date,
    starting_balance,
    events,
    minimum_balance,
    days=90
):

    request_date = pd.Timestamp(
        request_date
    ).normalize()

    events = events.copy()

    events["event_date"] = pd.to_datetime(
        events["event_date"]
    ).dt.normalize()

    forecast = []

    balance = float(starting_balance)


    for day in range(days + 1):

        current_date = (
            request_date
            + pd.Timedelta(days=day)
        )


        daily_events = events[
            events["event_date"] == current_date
        ]


        income = 0

        expenses = 0


        for _, event in daily_events.iterrows():

            amount = float(
                event["amount"]
            )


            if event["event_type"] == "income":

                income += amount


            elif event["event_type"] == "expense":

                expenses += amount


        balance += income

        balance -= expenses


        forecast.append({

            "date": current_date,

            "income": income,

            "expenses": expenses,

            "balance": balance,

            "safe": (
                balance >= minimum_balance
            )

        })


    return pd.DataFrame(forecast)


# =========================================================
# MINIMUM FORECAST BALANCE
# =========================================================

def minimum_forecast_balance(
    forecast
):

    return forecast["balance"].min()


# =========================================================
# CHECK WHETHER FORECAST IS SAFE
# =========================================================

def is_safe(
    forecast,
    minimum_balance
):

    return (
        forecast["balance"].min()
        >= float(minimum_balance)
    )


# =========================================================
# CALCULATE SAFE PURCHASE AMOUNT
# =========================================================

def calculate_safe_amount(
    request_date,
    starting_balance,
    requested_amount,
    events,
    minimum_balance
):

    safe_amount = 0

    requested_amount = int(
        float(requested_amount)
    )


    # Try each possible purchase amount

    for amount in range(
        0,
        requested_amount + 1
    ):

        balance_after_payment = (
            float(starting_balance)
            - amount
        )


        forecast = create_forecast(

            request_date,

            balance_after_payment,

            events,

            minimum_balance,

            days=90

        )


        if is_safe(
            forecast,
            minimum_balance
        ):

            safe_amount = amount

        else:

            # Once unsafe, larger amounts
            # will also be unsafe.

            break


    return safe_amount


# =========================================================
# FIND EARLIEST FULL PAYMENT DATE
# =========================================================

def find_earliest_full_payment_date(
    request_date,
    requested_amount,
    starting_balance,
    events,
    minimum_balance,
    days=90
):

    request_date = pd.Timestamp(
        request_date
    ).normalize()

    events = events.copy()

    events["event_date"] = pd.to_datetime(
        events["event_date"]
    ).dt.normalize()


    requested_amount = float(
        requested_amount
    )


    for day in range(days):

        test_date = (
            request_date
            + pd.Timedelta(days=day)
        )


        # Events before the purchase date
        previous_events = events[
            events["event_date"] < test_date
        ]


        balance = float(
            starting_balance
        )


        # Calculate balance available
        # on test date

        for _, event in previous_events.iterrows():

            amount = float(
                event["amount"]
            )


            if event["event_type"] == "income":

                balance += amount


            elif event["event_type"] == "expense":

                balance -= amount


        # Pay for the requested item

        balance_after_purchase = (
            balance
            - requested_amount
        )


        # Events from purchase date onward

        future_events = events[
            events["event_date"] >= test_date
        ].copy()


        forecast = create_forecast(

            test_date,

            balance_after_purchase,

            future_events,

            minimum_balance,

            days=90

        )


        if is_safe(
            forecast,
            minimum_balance
        ):

            return test_date


    return None


# =========================================================
# GET PAYMENT OPTIONS
# =========================================================

def get_payment_options(
    request_id,
    payment_options
):

    return payment_options[
        payment_options["request_id"]
        == request_id
    ].copy()


# =========================================================
# CHECK PAYMENT SCHEDULE
# =========================================================

def check_payment_schedule(
    schedule,
    request_date,
    starting_balance,
    events,
    minimum_balance
):

    balance = float(
        starting_balance
    )


    for payment_date, amount in schedule:

        forecast = create_forecast(

            request_date,

            balance,

            events,

            minimum_balance

        )


        matching = forecast[
            forecast["date"]
            == pd.Timestamp(payment_date).normalize()
        ]


        if matching.empty:

            return False


        balance = (
            matching.iloc[0]["balance"]
            - float(amount)
        )


        if balance < float(
            minimum_balance
        ):

            return False


    return True


# =========================================================
# ACCEPTS PAYMENT METHOD
# =========================================================

def accepts_payment_method(
    profile,
    method
):

    accepted = profile[
        "payment_methods_user_will_consider"
    ]

    return method in accepted