from flask import Flask, render_template, request
import sqlite3
import joblib
import math

from severity import analyze_severity

from response_recommendation import (
    get_recommendations
)

from emergency_resources import (
    get_location_coordinates,
    find_nearby_resources
)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

DATABASE = "resqai.db"


# ============================================================
# LOAD AI MODEL
# ============================================================

model = joblib.load(
    "incident_model.pkl"
)


# ============================================================
# GET COORDINATES
# ============================================================

def get_coordinates(
    location,
    latitude,
    longitude
):

    # --------------------------------------------------------
    # 1. Browser GPS
    # --------------------------------------------------------

    try:

        if (
            latitude is not None
            and longitude is not None
            and str(latitude).strip() != ""
            and str(longitude).strip() != ""
        ):

            lat = float(latitude)
            lon = float(longitude)

            if (
                -90 <= lat <= 90
                and -180 <= lon <= 180
                and not (
                    lat == 0
                    and lon == 0
                )
            ):

                return lat, lon

    except (
        ValueError,
        TypeError
    ):

        pass


    # --------------------------------------------------------
    # 2. USER ENTERED LOCATION
    # --------------------------------------------------------

    if location:

        lat, lon = (
            get_location_coordinates(
                location
            )
        )

        if (
            lat is not None
            and lon is not None
        ):

            return lat, lon


    # --------------------------------------------------------
    # 3. Nothing found
    # --------------------------------------------------------

    return None, None


# ============================================================
# DISTANCE
# ============================================================

def calculate_distance(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):

    earth_radius = 6371.0

    lat1 = math.radians(
        latitude1
    )

    lat2 = math.radians(
        latitude2
    )

    delta_lat = math.radians(
        latitude2 - latitude1
    )

    delta_lon = math.radians(
        longitude2 - longitude1
    )

    a = (
        math.sin(
            delta_lat / 2
        ) ** 2

        +

        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(
            delta_lon / 2
        ) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(
            1 - a
        )
    )

    return earth_radius * c


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# REPORT PAGE
# ============================================================

@app.route("/report")
def report():

    return render_template(
        "report.html"
    )


# ============================================================
# SUBMIT REPORT
# ============================================================

@app.route(
    "/submit-report",
    methods=["POST"]
)
def submit_report():

    # ========================================================
    # FORM DATA
    # ========================================================

    description = request.form.get(
        "description",
        ""
    ).strip()


    location = request.form.get(
        "location",
        ""
    ).strip()


    latitude_input = request.form.get(
        "latitude",
        ""
    ).strip()


    longitude_input = request.form.get(
        "longitude",
        ""
    ).strip()


    # ========================================================
    # VALIDATE DESCRIPTION
    # ========================================================

    if not description:

        return (
            "Emergency description is required.",
            400
        )


    # ========================================================
    # VALIDATE LOCATION
    # ========================================================

    if not location:

        return (
            "Emergency location is required.",
            400
        )


    # ========================================================
    # GET LOCATION COORDINATES
    # ========================================================

    latitude, longitude = get_coordinates(

        location,

        latitude_input,

        longitude_input

    )


    print("\n")
    print(
        "=" * 60
    )

    print(
        "RESQAI INCIDENT"
    )

    print(
        "=" * 60
    )

    print(
        "Description:",
        description
    )

    print(
        "User Location:",
        location
    )

    print(
        "Coordinates:",
        latitude,
        longitude
    )


    # ========================================================
    # AI INCIDENT PREDICTION
    # ========================================================

    try:

        prediction = model.predict(
            [description]
        )[0]

    except Exception as error:

        print(
            "Prediction error:",
            error
        )

        prediction = "Accident"


    prediction = str(
        prediction
    ).strip()


    print(
        "AI Incident Type:",
        prediction
    )


    # ========================================================
    # CONFIDENCE
    # ========================================================

    confidence = 0


    try:

        probabilities = (
            model.predict_proba(
                [description]
            )[0]
        )

        confidence = (
            max(probabilities)
            * 100
        )

    except Exception as error:

        print(
            "Confidence error:",
            error
        )


    # ========================================================
    # SEVERITY
    # ========================================================

    try:

        severity, priority = (
            analyze_severity(
                description
            )
        )

    except Exception as error:

        print(
            "Severity error:",
            error
        )

        severity = "High"
        priority = "P2"


    print(
        "Severity:",
        severity
    )

    print(
        "Priority:",
        priority
    )


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    try:

        recommendations = (
            get_recommendations(

                prediction,

                severity,

                description

            )
        )

    except Exception as error:

        print(
            "Recommendation error:",
            error
        )

        recommendations = []


    # ========================================================
    # EMERGENCY RESOURCES
    # ========================================================

    nearby_resources = []


    if (
        latitude is not None
        and longitude is not None
    ):

        try:

            nearby_resources = (
                find_nearby_resources(

                    latitude=latitude,

                    longitude=longitude,

                    radius=10000,

                    resource_type=prediction,

                    description=description

                )
            )

        except Exception as error:

            print(
                "Emergency resource error:",
                error
            )

            nearby_resources = []


    # ========================================================
    # CALCULATE DISTANCE
    # ========================================================

    for resource in nearby_resources:

        try:

            resource_latitude = float(
                resource["latitude"]
            )

            resource_longitude = float(
                resource["longitude"]
            )


            resource["distance"] = round(

                calculate_distance(

                    latitude,

                    longitude,

                    resource_latitude,

                    resource_longitude

                ),

                2

            )


        except (
            KeyError,
            TypeError,
            ValueError
        ):

            resource["distance"] = None


    # ========================================================
    # SORT NEAREST FIRST
    # ========================================================

    nearby_resources.sort(

        key=lambda resource:

        (
            resource.get(
                "distance"
            )

            if resource.get(
                "distance"
            ) is not None

            else float("inf")
        )

    )


    print(
        "Resources Found:",
        len(nearby_resources)
    )


    for resource in nearby_resources:

        print(
            "-",
            resource.get("name"),
            "|",
            resource.get("type"),
            "|",
            resource.get("distance"),
            "km",
            "|",
            resource.get("address")
        )


    # ========================================================
    # SAVE INCIDENT
    # ========================================================

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()


    try:

        cursor.execute("""
            INSERT INTO incidents
            (
                description,
                incident_type,
                severity,
                priority,
                location,
                latitude,
                longitude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (

            description,

            prediction,

            severity,

            priority,

            location,

            latitude,

            longitude

        ))


        connection.commit()


    except sqlite3.Error as error:

        print(
            "Database error:",
            error
        )


    finally:

        connection.close()


    # ========================================================
    # RESULT PAGE
    # ========================================================

    return render_template(

        "result.html",

        prediction=prediction,

        confidence=round(
            confidence,
            2
        ),

        severity=severity,

        priority=priority,

        location=location,

        description=description,

        recommendations=recommendations,

        nearby_resources=nearby_resources,

        latitude=latitude,

        longitude=longitude

    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()


    incidents = []

    total_incidents = 0

    critical_incidents = 0

    high_priority = 0


    try:

        # ----------------------------------------------------
        # INCIDENTS
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                description,
                incident_type,
                severity,
                priority,
                location,
                latitude,
                longitude,
                created_at
            FROM incidents
            ORDER BY created_at DESC
        """)

        incidents = cursor.fetchall()


        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM incidents
        """)

        total_incidents = (
            cursor.fetchone()[0]
        )


        # ----------------------------------------------------
        # CRITICAL
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM incidents
            WHERE severity = 'Critical'
        """)

        critical_incidents = (
            cursor.fetchone()[0]
        )


        # ----------------------------------------------------
        # P1
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM incidents
            WHERE priority = 'P1'
        """)

        high_priority = (
            cursor.fetchone()[0]
        )


    except sqlite3.Error as error:

        print(
            "Dashboard database error:",
            error
        )


    finally:

        connection.close()


    return render_template(

        "dashboard.html",

        incidents=incidents,

        total_incidents=total_incidents,

        critical_incidents=critical_incidents,

        high_priority=high_priority

    )


# ============================================================
# RESOURCE SEARCH PAGE
# ============================================================

@app.route("/resources")
def resources():

    location = request.args.get(
        "location",
        ""
    ).strip()


    incident_type = request.args.get(
        "incident_type",
        ""
    ).strip()


    description = request.args.get(
        "description",
        ""
    ).strip()


    latitude = None
    longitude = None

    nearby_resources = []


    # ========================================================
    # GEOCODE USER LOCATION
    # ========================================================

    if location:

        latitude, longitude = (
            get_location_coordinates(
                location
            )
        )


    # ========================================================
    # SEARCH
    # ========================================================

    if (
        latitude is not None
        and longitude is not None
    ):

        try:

            nearby_resources = (
                find_nearby_resources(

                    latitude=latitude,

                    longitude=longitude,

                    radius=10000,

                    resource_type=incident_type,

                    description=description

                )
            )

        except Exception as error:

            print(
                "Resource page error:",
                error
            )

            nearby_resources = []


    # ========================================================
    # DISTANCES
    # ========================================================

    for resource in nearby_resources:

        try:

            resource["distance"] = round(

                calculate_distance(

                    latitude,

                    longitude,

                    float(
                        resource["latitude"]
                    ),

                    float(
                        resource["longitude"]
                    )

                ),

                2

            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            resource["distance"] = None


    # ========================================================
    # SORT
    # ========================================================

    nearby_resources.sort(

        key=lambda resource:

        (
            resource.get(
                "distance"
            )

            if resource.get(
                "distance"
            ) is not None

            else float("inf")
        )

    )


    # ========================================================
    # RESULT
    # ========================================================

    return render_template(

        "resources.html",

        resources=nearby_resources,

        location=location,

        incident_type=incident_type,

        latitude=latitude,

        longitude=longitude

    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print("\n")
    print(
        "=" * 60
    )

    print(
        "RESQAI - AI EMERGENCY RESPONSE SYSTEM"
    )

    print(
        "=" * 60
    )

    print(
        "Server: http://127.0.0.1:5000"
    )

    print(
        "=" * 60
    )

    print("\n")


    app.run(
        debug=True
    )