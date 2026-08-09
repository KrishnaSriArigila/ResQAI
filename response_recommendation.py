# ============================================================
# RESQAI - RESPONSE RECOMMENDATION
# ============================================================


def get_recommendations(incident_type, severity, description):

    # Convert values to lowercase
    incident_type = str(incident_type or "").lower()
    severity = str(severity or "").lower()
    description = str(description or "").lower()


    recommendations = []


    # ========================================================
    # ACCIDENT
    # ========================================================

    if (
        "accident" in incident_type
        or "accident" in description
        or "collision" in description
        or "crash" in description
    ):

        recommendations.extend([

            "🚑 Contact emergency medical services",

            "🏥 Identify the nearest hospital",

            "🚨 Alert the nearby emergency response team",

            "🚗 Keep the accident area clear",

            "📍 Share the incident location with responders"

        ])


    # ========================================================
    # FIRE
    # ========================================================

    elif (
        "fire" in incident_type
        or "fire" in description
        or "burning" in description
    ):

        recommendations.extend([

            "🚒 Contact the fire and rescue service",

            "🚨 Alert nearby emergency responders",

            "🏃 Move people away from the affected area",

            "⚠️ Avoid entering the burning building",

            "📍 Share the incident location with responders"

        ])


    # ========================================================
    # MEDICAL EMERGENCY
    # ========================================================

    elif (
        "medical" in incident_type
        or "medical" in description
        or "injured" in description
        or "unconscious" in description
    ):

        recommendations.extend([

            "🚑 Contact emergency medical services",

            "🏥 Identify the nearest hospital",

            "🚨 Alert the nearby medical response team",

            "📍 Share the incident location",

            "👨‍⚕️ Provide first aid if it is safe to do so"

        ])


    # ========================================================
    # FLOOD
    # ========================================================

    elif (
        "flood" in incident_type
        or "flood" in description
        or "waterlogging" in description
    ):

        recommendations.extend([

            "🚨 Alert local emergency authorities",

            "🏃 Move people to a safe location",

            "🚧 Avoid flooded roads",

            "📍 Monitor the affected area",

            "⚠️ Avoid contact with electrical equipment"

        ])


    # ========================================================
    # GENERAL EMERGENCY
    # ========================================================

    else:

        recommendations.extend([

            "🚨 Alert the appropriate emergency response team",

            "📍 Verify the incident location",

            "📞 Contact the relevant emergency service",

            "⚠️ Keep people away from the affected area",

            "📋 Monitor the incident status"

        ])


    # ========================================================
    # CRITICAL INCIDENT
    # ========================================================

    if severity == "critical":

        recommendations.insert(
            0,
            "🔴 PRIORITY ACTION: Immediate emergency response required"
        )


    # ========================================================
    # HIGH PRIORITY INCIDENT
    # ========================================================

    elif severity == "high":

        recommendations.insert(
            0,
            "🟠 PRIORITY ACTION: Urgent response recommended"
        )


    return recommendations