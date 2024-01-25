import requests
import json


def get_car_distance_between(lon_1, lat_1, lon_2, lat_2):
    r = requests.get(f"https://router.project-osrm.org/route/v1/car/{lon_1},{lat_1};{lon_2},{lat_2}?overview=false""")
    routes = json.loads(r.content)
    return routes.get("routes")[0].get("distance")



