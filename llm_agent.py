import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from data_loader import load_data

from forecast import (
    calculate_safe_amount,
    find_earliest_full_payment_date
)

from payment_planner import (
    create_full_payment_plan,
    create_partial_payment_plan
)


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "dataset"


# =========================================================
# INITIALIZE GROQ LLM
# =========================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


# =========================================================
# LOAD ALL DATA
# =========================================================

(
    requests,
    sample_requests,
    profiles,
    events,
    exchange_rates,
    payment_options,
    messages,
    images
) = load_data()


# =========================================================
# CONVERT DATE COLUMNS
# =========================================================

events["event_date"] = pd.to_datetime(
    events["event_date"]
).dt.normalize()


requests["request_date"] = pd.to_datetime(
    requests["request_date"]
).dt.normalize()


requests["desired_completion_date"] = pd.to_datetime(
    requests["desired_completion_date"]
).dt.normalize()


# =========================================================
# ANALYZE USER MESSAGE USING LLM
# =========================================================

def analyze_message(message):

    prompt = f"""
You are a financial data extraction assistant.

Read the following message.

Extract only factual financial information.

Message:
{message}

Return exactly:

amount:
date:
action:
description:

Rules:

1. Extract only information explicitly mentioned.
2. Do not invent missing information.
3. Do not make a financial recommendation.
4. Do not say BUY or WAIT.
5. If a value is not available, write:
   not specified
"""

    response = llm.invoke(prompt)

    return response.content


# =========================================================
# GET EVENT IMAGE
# =========================================================

def get_event_image(
    event_id,
    images
):

    result = images[
        images["related_event_id"] == event_id
    ]

    if result.empty:
        return None

    return result.iloc[0]


# =========================================================
# CONVERT VALUE TO BOOLEAN
# =========================================================

def to_boolean(value):

    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return False

    value = str(value).strip().lower()

    return value in [
        "true",
        "1",
        "yes",
        "y"
    ]


# =========================================================
# GET USER PROFILE
# =========================================================

def get_user_profile(
    user_id
):

    result = profiles[
        profiles["user_id"] == user_id
    ]

    if result.empty:
        return None

    return result.iloc[0]


# =========================================================
# GET USER EVENTS
# =========================================================

def get_user_events(
    user_id
):

    user_events = events[
        events["user_id"] == user_id
    ].copy()

    return user_events


# =========================================================
# MAKE BUY / WAIT DECISION
# =========================================================

def make_decision(
    request,
    profile,
    user_events,
    payment_options
):

    # -----------------------------------------------------
    # Request information
    # -----------------------------------------------------

    request_date = pd.Timestamp(
        request["request_date"]
    ).normalize()


    requested_amount = float(
        request["requested_amount"]
    )


    desired_completion_date = pd.Timestamp(
        request["desired_completion_date"]
    ).normalize()


    allows_partial_payment = to_boolean(
        request["allows_partial_payment"]
    )


    # -----------------------------------------------------
    # User financial information
    # -----------------------------------------------------

    starting_balance = float(
        profile["current_available_balance"]
    )


    minimum_balance = float(
        profile["minimum_balance_to_keep"]
    )


    # -----------------------------------------------------
    # 1. Calculate maximum safe amount
    # -----------------------------------------------------

    amount_safe = calculate_safe_amount(

        request_date,

        starting_balance,

        requested_amount,

        user_events,

        minimum_balance

    )


    # -----------------------------------------------------
    # 2. Find earliest date for full payment
    # -----------------------------------------------------

    earliest_date = (
        find_earliest_full_payment_date(

            request_date,

            requested_amount,

            starting_balance,

            user_events,

            minimum_balance

        )
    )


    # -----------------------------------------------------
    # 3. BUY NOW
    # -----------------------------------------------------

    if amount_safe >= requested_amount:

        status = "affordable_now"

        method = "full_payment"


        plan = create_full_payment_plan(

            request_date,

            requested_amount

        )


        earliest = request_date


    # -----------------------------------------------------
    # 4. PARTIAL PAYMENT
    # -----------------------------------------------------

    elif (

        amount_safe > 0

        and allows_partial_payment

        and earliest_date is not None

        and earliest_date <= desired_completion_date

    ):

        status = "affordable_with_plan"

        method = "partial_payment"


        plan = create_partial_payment_plan(

            request_date,

            amount_safe,

            requested_amount,

            earliest_date

        )


        earliest = earliest_date


    # -----------------------------------------------------
    # 5. WAIT UNTIL AFFORDABLE
    # -----------------------------------------------------

    elif earliest_date is not None:

        status = "affordable_later"

        method = "wait"

        plan = "none"

        earliest = earliest_date


    # -----------------------------------------------------
    # 6. NOT AFFORDABLE
    # -----------------------------------------------------

    else:

        status = "not_affordable"

        method = "not_recommended"

        plan = "none"

        earliest = None


    # =====================================================
    # DECISION EXPLANATION
    # =====================================================

    if status == "affordable_now":

        explanation = (
            "The requested purchase is affordable now "
            "while maintaining the required minimum balance "
            "through the 90-day forecast."
        )


    elif status == "affordable_with_plan":

        explanation = (
            "The full purchase is not immediately affordable, "
            "but a partial payment is possible while maintaining "
            "the required minimum balance."
        )


    elif status == "affordable_later":

        explanation = (
            "The purchase is not currently affordable. "
            "The forecast indicates a future date when the "
            "full amount can be paid safely."
        )


    else:

        explanation = (
            "The requested purchase cannot be safely afforded "
            "within the 90-day financial forecast while "
            "maintaining the required minimum balance."
        )


    # =====================================================
    # RETURN DECISION
    # =====================================================

    return {

        "amount_safe_to_pay": round(
            amount_safe,
            2
        ),

        "affordability_status": status,

        "recommended_payment_method": method,

        "payment_plan": plan,

        "earliest_date_for_full_payment": earliest,

        "spending_changes_needed": "none",

        "decision_explanation": explanation

    }


# =========================================================
# PROCESS ALL REQUESTS
# =========================================================

def process_requests():

    results = []


    # -----------------------------------------------------
    # Process every purchase request
    # -----------------------------------------------------

    for _, request in requests.iterrows():

        request_id = request[
            "request_id"
        ]


        user_id = request[
            "user_id"
        ]


        print(
            f"\nProcessing request: {request_id}"
        )


        # -------------------------------------------------
        # Get user profile
        # -------------------------------------------------

        profile = get_user_profile(
            user_id
        )


        if profile is None:

            print(
                f"Profile not found for user: {user_id}"
            )

            continue


        # -------------------------------------------------
        # Get financial events
        # -------------------------------------------------

        user_events = get_user_events(
            user_id
        )


        # -------------------------------------------------
        # Make decision
        # -------------------------------------------------

        result = make_decision(

            request,

            profile,

            user_events,

            payment_options

        )


        # -------------------------------------------------
        # Add request ID
        # -------------------------------------------------

        result["request_id"] = request_id


        # -------------------------------------------------
        # Add result
        # -------------------------------------------------

        results.append(
            result
        )


        print(
            f"Status: "
            f"{result['affordability_status']}"
        )

        print(
            f"Method: "
            f"{result['recommended_payment_method']}"
        )


    return pd.DataFrame(
        results
    )


# =========================================================
# GENERATE OUTPUT
# =========================================================

def generate_output():

    output = process_requests()


    # -----------------------------------------------------
    # Required output columns
    # -----------------------------------------------------

    output = output[
        [
            "request_id",
            "amount_safe_to_pay",
            "affordability_status",
            "recommended_payment_method",
            "payment_plan",
            "earliest_date_for_full_payment",
            "spending_changes_needed",
            "decision_explanation"
        ]
    ]


    # -----------------------------------------------------
    # Output file path
    # -----------------------------------------------------

    output_path = (
        DATASET_PATH / "output.csv"
    )


    # -----------------------------------------------------
    # Save CSV
    # -----------------------------------------------------

    output.to_csv(
        output_path,
        index=False
    )


    # -----------------------------------------------------
    # Display result
    # -----------------------------------------------------

    print("\n")
    print("=" * 60)
    print("BUY OR WAIT RESULTS")
    print("=" * 60)

    print(
        output.to_string(
            index=False
        )
    )


    print("\n")
    print("=" * 60)
    print("OUTPUT GENERATED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"Output file: {output_path}"
    )


    return output


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    generate_output()