import pandas as pd

from data_loader import load_data
from llm_agent import make_decision
from validator import validate_output


# =========================================================
# MAIN FUNCTION
# =========================================================

def main():

    print("================================")
    print("      BUY OR WAIT AGENT")
    print("================================")


    # =====================================================
    # 1. LOAD ALL DATA
    # =====================================================

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


    print("\nData loaded successfully.")


    # =====================================================
    # 2. CONVERT DATE COLUMNS
    # =====================================================

    requests["request_date"] = pd.to_datetime(
        requests["request_date"]
    ).dt.normalize()


    requests["desired_completion_date"] = pd.to_datetime(
        requests["desired_completion_date"]
    ).dt.normalize()


    events["event_date"] = pd.to_datetime(
        events["event_date"]
    ).dt.normalize()


    # =====================================================
    # 3. PROCESS REQUESTS
    # =====================================================

    results = []


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

        user_profile = profiles[
            profiles["user_id"] == user_id
        ]


        if user_profile.empty:

            print(
                f"Profile not found for {user_id}"
            )

            continue


        profile = user_profile.iloc[0]


        # -------------------------------------------------
        # Get user's financial events
        # -------------------------------------------------

        user_events = events[
            events["user_id"] == user_id
        ].copy()


        # -------------------------------------------------
        # Make BUY / WAIT decision
        # -------------------------------------------------

        decision = make_decision(

            request,

            profile,

            user_events,

            payment_options

        )


        # -------------------------------------------------
        # Add request ID
        # -------------------------------------------------

        decision["request_id"] = (
            request_id
        )


        results.append(
            decision
        )


        print(
            f"Decision: "
            f"{decision['affordability_status']}"
        )


    # =====================================================
    # 4. CREATE OUTPUT DATAFRAME
    # =====================================================

    output = pd.DataFrame(
        results
    )


    # -----------------------------------------------------
    # Check whether results exist
    # -----------------------------------------------------

    if output.empty:

        print(
            "\nNo decisions were generated."
        )

        return


    # =====================================================
    # 5. REQUIRED OUTPUT COLUMNS
    # =====================================================

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


    # -----------------------------------------------------
    # Check missing columns
    # -----------------------------------------------------

    missing_columns = [

        column

        for column in required_columns

        if column not in output.columns

    ]


    if missing_columns:

        print(
            "\nMissing output columns:"
        )

        for column in missing_columns:

            print(
                f" - {column}"
            )

        return


    output = output[
        required_columns
    ]


    # =====================================================
    # 6. VALIDATE OUTPUT
    # =====================================================

    errors = validate_output(
        output,
        requests
    )


    if errors:

        print("\n================================")
        print("VALIDATION ERRORS")
        print("================================")


        for error in errors:

            print(
                f"- {error}"
            )


        return


    # =====================================================
    # 7. SAVE OUTPUT
    # =====================================================

    from pathlib import Path


    BASE_DIR = Path(
        __file__
    ).resolve().parent.parent


    output_path = (
        BASE_DIR
        / "dataset"
        / "output.csv"
    )


    output.to_csv(
        output_path,
        index=False
    )


    # =====================================================
    # 8. DISPLAY SUCCESS
    # =====================================================

    print("\n================================")
    print("SUCCESS!")
    print("================================")


    print(
        f"Processed {len(output)} requests."
    )


    print(
        f"Created: {output_path}"
    )


    print("\nFinal Output:\n")

    print(
        output.to_string(
            index=False
        )
    )


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()