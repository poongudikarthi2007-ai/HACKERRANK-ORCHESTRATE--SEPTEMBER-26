import pandas as pd

from data_loader import load_data


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
# GET USER PROFILE
# =========================================================

def get_user_profile(user_id, profiles):

    user_profile = profiles[
        profiles["user_id"] == user_id
    ]

    if user_profile.empty:
        return None

    return user_profile.iloc[0]


# =========================================================
# GET USER
# =========================================================

user = get_user_profile(
    "user_001",
    profiles
)

print("USER PROFILE")
print(user)


# =========================================================
# CONVERT DATE COLUMNS
# =========================================================

events["event_date"] = pd.to_datetime(
    events["event_date"]
)

requests["request_date"] = pd.to_datetime(
    requests["request_date"]
)

requests["desired_completion_date"] = pd.to_datetime(
    requests["desired_completion_date"]
)


# =========================================================
# CHECK DATE TYPE
# =========================================================

print("\nRequest Date Data Type:")

print(
    requests["request_date"].dtype
)