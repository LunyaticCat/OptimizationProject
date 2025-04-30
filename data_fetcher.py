import requests

from aircraft import LandingTime, AircraftLanding

def order_data(flat_data: list):
    pointer = 0

    n_aircraft = int(flat_data[pointer])
    pointer += 1
    freeze_time = flat_data[pointer]
    pointer += 1

    n_runway = 1
    landing_times = []
    separation_times = [[] for _ in range(n_aircraft)]

    for i in range(n_aircraft):
        lt = LandingTime(flat_data[pointer],
                         flat_data[pointer + 1],
                         flat_data[pointer + 2],
                         flat_data[pointer + 3],
                         flat_data[pointer + 4],
                         flat_data[pointer + 5])
        landing_times.append(lt)
        pointer += 6

        sep_times = flat_data[pointer:pointer + n_aircraft]
        separation_times[i].extend(sep_times)
        pointer += n_aircraft

    aircraft_landing = AircraftLanding(n_aircraft, n_runway, freeze_time, landing_times, separation_times)
    return aircraft_landing

def flatten_data(nested_data):
    return [item for sublist in nested_data for item in sublist]


def fetch_data(url: str):
    response = requests.get(url)
    response.raise_for_status()

    data = [[float(x.strip()) for x in line.split()] for line in response.text.splitlines()]

    flat_data = flatten_data(data)

    return flat_data

def fetch_aircraft_data():
    data = []
    for i in range(12):
        data.append(order_data(fetch_data(f"https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/airland{i+1}.txt")))
    return data