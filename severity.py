def analyze_severity(description):

    text = description.lower()

    critical_keywords = [
        "people trapped",
        "person trapped",
        "multiple injured",
        "multiple people injured",
        "dead",
        "death",
        "unconscious",
        "not breathing",
        "massive fire",
        "building collapse",
        "explosion",
        "bomb"
    ]

    high_keywords = [
        "serious injury",
        "severely injured",
        "heavy fire",
        "major accident",
        "major fire",
        "critical",
        "bleeding",
        "ambulance needed",
        "urgent"
    ]

    medium_keywords = [
        "injured",
        "accident",
        "fire",
        "smoke",
        "flood",
        "robbery",
        "theft"
    ]


    # Critical
    for keyword in critical_keywords:

        if keyword in text:

            return "Critical", "P1"


    # High
    for keyword in high_keywords:

        if keyword in text:

            return "High", "P1"


    # Medium
    for keyword in medium_keywords:

        if keyword in text:

            return "Medium", "P2"


    # Default
    return "Low", "P3"