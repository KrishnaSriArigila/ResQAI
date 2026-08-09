from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib


# Training examples
texts = [

    # Accident
    "There was a car accident on the highway",
    "A major road accident has occurred",
    "Two vehicles collided near the junction",
    "A person was injured in a traffic accident",
    "Multiple vehicles crashed on the road",
    "There has been a serious vehicle collision",

    # Fire
    "There is a fire in the building",
    "A house is burning",
    "Fire broke out in the shopping mall",
    "There is smoke and flames coming from a building",
    "A major fire has been reported",
    "The building caught fire",

    # Medical
    "A person is unconscious and needs medical help",
    "Someone has collapsed and needs an ambulance",
    "A person is seriously injured",
    "Medical emergency at the railway station",
    "Someone is having difficulty breathing",
    "An injured person needs immediate medical attention",

    # Crime
    "Someone is being attacked",
    "There is a robbery happening",
    "A person is threatening people",
    "Someone broke into the house",
    "There is a fight happening in the street",
    "A suspicious person is threatening people",

    # Flood
    "The road is completely flooded",
    "Heavy rain has caused flooding",
    "Water has entered several houses",
    "The area is experiencing severe flooding",
    "Flood water is blocking the road",
    "The river has overflowed and flooded the area"
]


labels = [

    # Accident
    "Accident", "Accident", "Accident",
    "Accident", "Accident", "Accident",

    # Fire
    "Fire", "Fire", "Fire",
    "Fire", "Fire", "Fire",

    # Medical
    "Medical", "Medical", "Medical",
    "Medical", "Medical", "Medical",

    # Crime
    "Crime", "Crime", "Crime",
    "Crime", "Crime", "Crime",

    # Flood
    "Flood", "Flood", "Flood",
    "Flood", "Flood", "Flood"
]


# Create machine learning pipeline
model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            stop_words="english"
        )
    ),

    (
        "classifier",
        LogisticRegression()
    )
])


# Train the model
model.fit(texts, labels)


# Save trained model
joblib.dump(model, "incident_model.pkl")


print("AI incident classification model trained successfully!")
print("Model saved as incident_model.pkl")