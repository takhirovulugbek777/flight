import math


def haversine(coord1, coord2):
    lat1, lon1 = map(lambda x: float(x.strip()), coord1.split(','))
    lat2, lon2 = map(lambda x: float(x.strip()), coord2.split(','))
    R = 6371

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return round(distance, 2)
