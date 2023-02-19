from requests import Session
from math import radians, sin, cos, asin, sqrt, inf


class Vehicle:

    def __init__(
        self,
        **kwargs
    ):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return f"<Vehicle: {self.name} {self.model} {self.year} {self.color} {self.price}>"


class VehicleManager:

    def __init__(self, url):
        self.session = Session()
        self.url = url + "/vehicles"

    def _request(self, method, data=None, id=None):
        if id != None:
            url = self.url+f"/{id}"
        else:
            url = self.url
        response = self.session.request(
            method, url, data=data, timeout=5)
        if response.status_code in [200, 201, 204]:
            return response
        else:
            response.raise_for_status()

    def _filter(self, vehicle, params={}):
        if params:
            for param in params:
                if getattr(vehicle, param) != params[param]:
                    return False
        return True

    def _get_distance(self, v1, v2):
        lo1 = radians(v1.longitude)
        lo2 = radians(v2.longitude)
        la1 = radians(v1.latitude)
        la2 = radians(v2.latitude)
        P = sin((la2 - la1) / 2)**2 + cos(la1) * \
            cos(la2) * sin((lo2 - lo1) / 2)**2
        Q = 2 * asin(sqrt(P))
        R_m = 6_371_000
        return (Q * R_m)

    def get_vehicles(self):
        response = self._request("GET")
        return [Vehicle(**car) for car in response.json()]

    def filter_vehicles(self, params={}):
        vehicles = self.get_vehicles()
        res = []
        for vehicle in vehicles:
            if self._filter(vehicle, params):
                res.append(vehicle)
        return res

    def get_vehicle(self, vehicle_id: int):
        response = self._request("GET", id=int(vehicle_id))
        return Vehicle(**response.json())

    def add_vehicle(self, vehicle: Vehicle):
        if type(vehicle) != Vehicle:
            return ValueError("vehicle must be object of Vehicle type")
        response = self._request("POST", data=vars(vehicle))
        return Vehicle(**response.json())

    def update_vehicle(self, vehicle):
        if type(vehicle) != Vehicle:
            return ValueError("vehicle must be object of Vehicle type")
        response = self._request(
            "PUT", data=vars(vehicle), id=int(vehicle.id))
        return Vehicle(**response.json())

    def delete_vehicle(self, id: int):
        self._request("DELETE", id=int(id))
        return

    def get_distance(self, id1: int, id2: int):
        v1 = self.get_vehicle(id1)
        v2 = self.get_vehicle(id2)
        return self._get_distance(v1, v2)

    def get_nearest_vehicle(self, id: int):
        if type(id) != int or id <= 0:
            raise ValueError("Id must be natural number")
        vehicles = self.get_vehicles()
        if len(vehicles) <= id:
            raise ValueError(f"Vehicle with {id} doesn't exist")
        target = vehicles[id-1]
        min_distance = inf
        closest = None
        for i in range(len(vehicles)):
            if i == id - 1:
                continue
            temp_distance = self._get_distance(target, vehicles[i])
            if temp_distance < min_distance:
                min_distance, closest = temp_distance, i
        if closest == None:
            return closest
        return vehicles[closest]

    def close(self):
        self.session.close()
