import joblib


# Load the trained AI model
model = joblib.load("incident_model.pkl")


# Emergency reports to test
test_cases = [
    "A car crashed into another vehicle and two people are injured",

    "A building is burning and there is heavy smoke",

    "Someone has collapsed and needs an ambulance",

    "There is a robbery happening near the bank",

    "Heavy rain has caused severe flooding"
]


# Test each emergency
for text in test_cases:

    prediction = model.predict([text])[0]

    probability = max(
        model.predict_proba([text])[0]
    )

    print()
    print("Emergency:", text)
    print("Predicted Type:", prediction)
    print(
        "Confidence:",
        round(probability * 100, 2),
        "%"
    )
    print("-" * 60)