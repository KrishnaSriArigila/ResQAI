import requests
import time
import math


# ============================================================
# RESQAI - EMERGENCY RESOURCE SEARCH
# ============================================================
#
# Dynamic location-based emergency resource search.
#
# Uses:
#   Nominatim  -> location geocoding + address fallback
#   Overpass   -> Police / Fire / Hospital / Clinic search
#
# IMPORTANT:
#   Search is ALWAYS centered on the user's coordinates.
#   Search radius is STRICT.
#   No automatic expansion to another city.
#
# Supported:
#   Police Stations
#   Fire Stations
#   Hospitals
#   Clinics
# ============================================================


# ============================================================
# API CONFIGURATION
# ============================================================

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

NOMINATIM_REVERSE_URL = (
    "https://nominatim.openstreetmap.org/reverse"
)

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


HEADERS = {
    "User-Agent": "ResQAI Emergency Response Project/1.0"
}


# ============================================================
# REQUEST SETTINGS
# ============================================================

GEOCODE_TIMEOUT = 15
REVERSE_TIMEOUT = 15
OVERPASS_TIMEOUT = 30

# Search only within 10 km
DEFAULT_RADIUS = 10000

# IMPORTANT:
# Do NOT expand to 25 km.
MAX_RADIUS = 10000


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def calculate_distance(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):

    earth_radius = 6371.0

    lat1 = math.radians(latitude1)
    lat2 = math.radians(latitude2)

    delta_lat = math.radians(
        latitude2 - latitude1
    )

    delta_lon = math.radians(
        longitude2 - longitude1
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


# ============================================================
# GET LOCATION COORDINATES
# ============================================================

def get_location_coordinates(location):

    """
    Convert user-entered location into latitude/longitude.

    Examples:

        Peddapuram
        Samalkota
        Kakinada
        Hyderabad
        Vijayawada
        Visakhapatnam

    Returns:

        (latitude, longitude)

    or:

        (None, None)
    """

    if not location:
        return None, None

    location = str(location).strip()

    if not location:
        return None, None

    # --------------------------------------------------------
    # If user entered coordinates directly
    # --------------------------------------------------------

    try:

        parts = location.split(",")

        if len(parts) == 2:

            lat = float(parts[0].strip())
            lon = float(parts[1].strip())

            if (
                -90 <= lat <= 90
                and
                -180 <= lon <= 180
            ):

                return lat, lon

    except (
        ValueError,
        TypeError
    ):

        pass

    # --------------------------------------------------------
    # Nominatim search
    # --------------------------------------------------------

    search_queries = [
        location,
        location + ", Andhra Pradesh, India",
        location + ", India"
    ]

    for query in search_queries:

        try:

            response = requests.get(

                NOMINATIM_URL,

                params={
                    "q": query,
                    "format": "json",
                    "limit": 5,
                    "countrycodes": "in",
                    "addressdetails": 1
                },

                headers=HEADERS,

                timeout=GEOCODE_TIMEOUT
            )

            if response.status_code != 200:
                continue

            results = response.json()

            if not results:
                continue

            for result in results:

                try:

                    lat = float(
                        result["lat"]
                    )

                    lon = float(
                        result["lon"]
                    )

                    if (
                        -90 <= lat <= 90
                        and
                        -180 <= lon <= 180
                    ):

                        print(
                            "Location found:",
                            result.get(
                                "display_name",
                                query
                            )
                        )

                        print(
                            "Coordinates:",
                            lat,
                            lon
                        )

                        return lat, lon

                except (
                    KeyError,
                    ValueError,
                    TypeError
                ):

                    continue

        except requests.RequestException as error:

            print(
                "Geocoding error:",
                error
            )

            continue

        # Respect Nominatim usage policy
        time.sleep(1)

    return None, None


# ============================================================
# DETERMINE RESOURCE TYPES
# ============================================================

def get_resource_filters(
    resource_type=None,
    description=""
):

    incident = (
        str(resource_type or "")
        + " "
        + str(description or "")
    ).lower()

    # --------------------------------------------------------
    # Police / Crime
    # --------------------------------------------------------

    police_words = [

        "robbery",
        "robber",
        "theft",
        "stolen",
        "crime",
        "criminal",
        "attack",
        "assault",
        "murder",
        "fight",
        "violence",
        "kidnap",
        "kidnapping",
        "burglary",
        "threat",
        "weapon",
        "police"

    ]

    # --------------------------------------------------------
    # Fire
    # --------------------------------------------------------

    fire_words = [

        "fire",
        "burning",
        "flames",
        "smoke",
        "explosion",
        "blast"

    ]

    # --------------------------------------------------------
    # Medical
    # --------------------------------------------------------

    medical_words = [

        "medical",
        "injury",
        "injured",
        "accident",
        "ambulance",
        "hospital",
        "clinic",
        "bleeding",
        "unconscious",
        "heart",
        "breathing",
        "fracture",
        "pain",
        "emergency",
        "patient"

    ]

    # --------------------------------------------------------
    # Determine category
    # --------------------------------------------------------

    if any(
        word in incident
        for word in police_words
    ):

        return ["police"]

    if any(
        word in incident
        for word in fire_words
    ):

        return ["fire_station"]

    if any(
        word in incident
        for word in medical_words
    ):

        return [
            "hospital",
            "clinic"
        ]

    # --------------------------------------------------------
    # Unknown incident
    # --------------------------------------------------------

    return [
        "police",
        "fire_station",
        "hospital",
        "clinic"
    ]


# ============================================================
# BUILD OVERPASS QUERY
# ============================================================

def build_overpass_query(
    latitude,
    longitude,
    radius,
    resource_filters
):

    queries = []

    for resource_type in resource_filters:

        if resource_type == "police":

            queries.append(
                f"""
                nwr(
                    around:{radius},
                    {latitude},
                    {longitude}
                )[
                    amenity=police
                ];
                """
            )

        elif resource_type == "fire_station":

            queries.append(
                f"""
                nwr(
                    around:{radius},
                    {latitude},
                    {longitude}
                )[
                    amenity=fire_station
                ];
                """
            )

        elif resource_type == "hospital":

            queries.append(
                f"""
                nwr(
                    around:{radius},
                    {latitude},
                    {longitude}
                )[
                    amenity=hospital
                ];
                """
            )

        elif resource_type == "clinic":

            queries.append(
                f"""
                nwr(
                    around:{radius},
                    {latitude},
                    {longitude}
                )[
                    amenity=clinic
                ];
                """
            )

    query = f"""
    [out:json][timeout:25];

    (
        {"".join(queries)}
    );

    out center tags;
    """

    return query


# ============================================================
# GET ELEMENT COORDINATES
# ============================================================

def get_element_coordinates(element):

    try:

        # OSM node

        if (
            element.get("lat") is not None
            and
            element.get("lon") is not None
        ):

            return (
                float(element["lat"]),
                float(element["lon"])
            )

        # OSM way/relation

        center = element.get("center")

        if center:

            if (
                center.get("lat") is not None
                and
                center.get("lon") is not None
            ):

                return (
                    float(center["lat"]),
                    float(center["lon"])
                )

    except (
        ValueError,
        TypeError
    ):

        pass

    return None, None


# ============================================================
# GET RESOURCE NAME
# ============================================================

def get_resource_name(
    tags,
    resource_type
):

    name = (
        tags.get("name")
        or
        tags.get("official_name")
        or
        tags.get("short_name")
    )

    if name:
        return name

    if resource_type == "police":
        return "Police Station"

    if resource_type == "fire_station":
        return "Fire Station"

    if resource_type == "hospital":
        return "Hospital"

    if resource_type == "clinic":
        return "Clinic"

    return "Emergency Resource"


# ============================================================
# BUILD ADDRESS FROM OSM TAGS
# ============================================================

def get_resource_address(tags):

    """
    Build the best possible address from OSM tags.
    """

    parts = []

    # --------------------------------------------------------
    # Full address
    # --------------------------------------------------------

    full_address = tags.get("addr:full")

    if full_address:

        return str(
            full_address
        ).strip()

    # --------------------------------------------------------
    # House number + street
    # --------------------------------------------------------

    house_number = tags.get(
        "addr:housenumber"
    )

    street = tags.get(
        "addr:street"
    )

    if house_number and street:

        parts.append(
            f"{house_number} {street}"
        )

    elif street:

        parts.append(
            street
        )

    # --------------------------------------------------------
    # Locality information
    # --------------------------------------------------------

    locality_keys = [

        "addr:neighbourhood",
        "addr:suburb",
        "addr:village",
        "addr:town",
        "addr:city",
        "addr:district"

    ]

    for key in locality_keys:

        value = tags.get(key)

        if (
            value
            and
            value not in parts
        ):

            parts.append(
                str(value).strip()
            )

    # --------------------------------------------------------
    # State
    # --------------------------------------------------------

    state = tags.get(
        "addr:state"
    )

    if (
        state
        and
        state not in parts
    ):

        parts.append(
            str(state).strip()
        )

    # --------------------------------------------------------
    # Pincode
    # --------------------------------------------------------

    postcode = tags.get(
        "addr:postcode"
    )

    if (
        postcode
        and
        postcode not in parts
    ):

        parts.append(
            str(postcode).strip()
        )

    if parts:

        return ", ".join(parts)

    return ""


# ============================================================
# REVERSE GEOCODING ADDRESS FALLBACK
# ============================================================

def reverse_geocode_address(
    latitude,
    longitude
):

    """
    Get readable address using the resource's
    exact latitude and longitude.
    """

    try:

        response = requests.get(

            NOMINATIM_REVERSE_URL,

            params={
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "zoom": 18,
                "addressdetails": 1
            },

            headers=HEADERS,

            timeout=REVERSE_TIMEOUT
        )

        if response.status_code != 200:

            return ""

        data = response.json()

        # ----------------------------------------------------
        # Complete display address
        # ----------------------------------------------------

        display_name = data.get(
            "display_name"
        )

        if display_name:

            return str(
                display_name
            ).strip()

        # ----------------------------------------------------
        # Construct address manually
        # ----------------------------------------------------

        address = data.get(
            "address",
            {}
        )

        parts = []

        address_keys = [

            "house_number",
            "road",
            "neighbourhood",
            "suburb",
            "village",
            "town",
            "city",
            "district",
            "state",
            "postcode"

        ]

        for key in address_keys:

            value = address.get(
                key
            )

            if (
                value
                and
                value not in parts
            ):

                parts.append(
                    str(value).strip()
                )

        if parts:

            return ", ".join(parts)

    except (
        requests.RequestException,
        ValueError,
        TypeError
    ) as error:

        print(
            "Reverse geocoding error:",
            error
        )

    return ""


# ============================================================
# GET FINAL RESOURCE ADDRESS
# ============================================================

def get_final_resource_address(
    tags,
    latitude,
    longitude
):

    """
    Address priority:

    1. OSM address tags
    2. Reverse geocoding
    3. OSM description
    4. OSM operator
    5. Final fallback
    """

    # --------------------------------------------------------
    # First: OSM address
    # --------------------------------------------------------

    address = get_resource_address(
        tags
    )

    if address:

        return address

    # --------------------------------------------------------
    # Second: reverse geocoding
    # --------------------------------------------------------

    address = reverse_geocode_address(

        latitude,
        longitude

    )

    if address:

        return address

    # --------------------------------------------------------
    # Third: description
    # --------------------------------------------------------

    description = tags.get(
        "description"
    )

    if description:

        return str(
            description
        ).strip()

    # --------------------------------------------------------
    # Fourth: operator
    # --------------------------------------------------------

    operator = tags.get(
        "operator"
    )

    if operator:

        return str(
            operator
        ).strip()

    # --------------------------------------------------------
    # Final fallback
    # --------------------------------------------------------

    return "Address not available"


# ============================================================
# NORMALIZE RESOURCE TYPE
# ============================================================

def normalize_resource_type(tags):

    amenity = (
        tags.get("amenity")
        or
        ""
    ).lower()

    if amenity == "police":

        return "Police Station"

    if amenity == "fire_station":

        return "Fire Station"

    if amenity == "hospital":

        return "Hospital"

    if amenity == "clinic":

        return "Clinic"

    return "Emergency Resource"


# ============================================================
# SEARCH OVERPASS
# ============================================================

def query_overpass(
    query
):

    """
    Try multiple Overpass servers.
    """

    for server in OVERPASS_URLS:

        try:

            print(
                "Searching emergency resources using:",
                server
            )

            response = requests.post(

                server,

                data=query,

                headers=HEADERS,

                timeout=OVERPASS_TIMEOUT
            )

            if response.status_code != 200:

                print(
                    "Overpass status:",
                    response.status_code
                )

                continue

            data = response.json()

            return data.get(
                "elements",
                []
            )

        except (
            requests.RequestException,
            ValueError
        ) as error:

            print(
                "Overpass error:",
                error
            )

            continue

    return []


# ============================================================
# FIND NEARBY RESOURCES
# ============================================================

def find_nearby_resources(
    latitude,
    longitude,
    radius=10000,
    resource_type=None,
    description=""
):

    """
    Find emergency resources around the user's
    exact latitude and longitude.

    IMPORTANT:
        Search radius is STRICT.
        No automatic expansion.
    """

    # --------------------------------------------------------
    # Validate coordinates
    # --------------------------------------------------------

    try:

        latitude = float(latitude)
        longitude = float(longitude)

    except (
        ValueError,
        TypeError
    ):

        return []

    if not (
        -90 <= latitude <= 90
        and
        -180 <= longitude <= 180
    ):

        return []

    # --------------------------------------------------------
    # Determine categories
    # --------------------------------------------------------

    resource_filters = get_resource_filters(

        resource_type,

        description

    )

    # --------------------------------------------------------
    # Radius
    # --------------------------------------------------------

    try:

        radius = int(radius)

    except (
        ValueError,
        TypeError
    ):

        radius = DEFAULT_RADIUS

    # STRICT MAXIMUM
    radius = max(
        1000,
        min(radius, MAX_RADIUS)
    )

    # --------------------------------------------------------
    # Search Overpass
    # --------------------------------------------------------

    query = build_overpass_query(

        latitude,

        longitude,

        radius,

        resource_filters

    )

    elements = query_overpass(
        query
    )

    # --------------------------------------------------------
    # Convert resources
    # --------------------------------------------------------

    resources = []

    seen = set()

    for element in elements:

        tags = element.get(
            "tags",
            {}
        )

        resource_latitude, resource_longitude = (
            get_element_coordinates(
                element
            )
        )

        if (
            resource_latitude is None
            or
            resource_longitude is None
        ):

            continue

        # ----------------------------------------------------
        # Calculate exact distance
        # ----------------------------------------------------

        distance = calculate_distance(

            latitude,
            longitude,

            resource_latitude,
            resource_longitude

        )

        # ----------------------------------------------------
        # STRICT RADIUS CHECK
        #
        # Nothing outside the requested radius can appear.
        # ----------------------------------------------------

        if distance * 1000 > radius:

            continue

        # ----------------------------------------------------
        # Resource type
        # ----------------------------------------------------

        resource_type_name = (
            normalize_resource_type(
                tags
            )
        )

        # ----------------------------------------------------
        # Resource name
        # ----------------------------------------------------

        name = get_resource_name(

            tags,

            tags.get(
                "amenity",
                ""
            )

        )

        # ----------------------------------------------------
        # ADDRESS
        # ----------------------------------------------------

        address = get_final_resource_address(

            tags,

            resource_latitude,

            resource_longitude

        )

        # ----------------------------------------------------
        # Remove duplicates
        # ----------------------------------------------------

        unique_key = (

            name.lower(),

            round(
                resource_latitude,
                5
            ),

            round(
                resource_longitude,
                5
            )

        )

        if unique_key in seen:

            continue

        seen.add(
            unique_key
        )

        # ----------------------------------------------------
        # Resource object
        # ----------------------------------------------------

        resource = {

            "name": name,

            "type": resource_type_name,

            "address": address,

            "latitude": resource_latitude,

            "longitude": resource_longitude,

            "distance": round(
                distance,
                2
            ),

            "phone": (
                tags.get("phone")
                or
                tags.get("contact:phone")
                or
                ""
            ),

            "website": (
                tags.get("website")
                or
                tags.get("contact:website")
                or
                ""
            ),

            "opening_hours": (
                tags.get("opening_hours")
                or
                ""
            ),

            "osm_id": element.get(
                "id"
            )

        }

        resources.append(
            resource
        )

    # --------------------------------------------------------
    # Sort nearest first
    # --------------------------------------------------------

    resources.sort(

        key=lambda item:

        item.get(
            "distance",
            float("inf")
        )

    )

    # --------------------------------------------------------
    # Maximum 20 resources
    # --------------------------------------------------------

    resources = resources[:20]

    # --------------------------------------------------------
    # Debug information
    # --------------------------------------------------------

    print(
        "------------------------------------------"
    )

    print(
        "Emergency Resource Search"
    )

    print(
        "Center:",
        latitude,
        longitude
    )

    print(
        "Incident:",
        resource_type
    )

    print(
        "Search categories:",
        resource_filters
    )

    print(
        "Search radius:",
        radius,
        "meters"
    )

    print(
        "Resources found:",
        len(resources)
    )

    for resource in resources:

        print(

            resource["name"],
            "|",

            resource["type"],
            "|",

            resource["distance"],
            "km |",

            resource["address"]

        )

    print(
        "------------------------------------------"
    )

    return resources


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\nTesting Peddapuram..."
    )

    lat, lon = get_location_coordinates(
        "Peddapuram, Andhra Pradesh"
    )

    print(
        "Coordinates:",
        lat,
        lon
    )

    if (
        lat is not None
        and
        lon is not None
    ):

        results = find_nearby_resources(

            latitude=lat,

            longitude=lon,

            radius=10000,

            resource_type="Robbery",

            description=(
                "There was a robbery. "
                "Please send police."
            )

        )

        print(
            "\nResults:"
        )

        for item in results:

            print(

                item["name"],
                "|",

                item["type"],
                "|",

                item["distance"],
                "km |",

                item["address"]

            )