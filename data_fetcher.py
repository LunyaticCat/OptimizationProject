import requests

from aircraft import LandingTime, AircraftLanding

def order_data(flat_data: list):
    """
    Orders and structures flat aircraft landing data into an AircraftLanding object.

    Args:
        flat_data (list): A flattened list of input data, parsed from text file.

    Returns:
        AircraftLanding: An instance of the AircraftLanding class containing parsed and organized data.
    """

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
    """
    Flattens a nested list of data into a single list.

    Args:
        nested_data (list of lists): A list of lists to be flattened.

    Returns:
        list: A single flattened list containing all elements from the nested list.
    """

    return [item for sublist in nested_data for item in sublist]


def fetch_data(url: str):
    """
    Fetches and flattens aircraft landing problem data from a remote URL.

    Args:
        url (str): The URL pointing to the raw aircraft landing data.

    Returns:
        list: A flattened list of float values extracted from the text data at the URL.
    """

    response = requests.get(url)
    response.raise_for_status()

    data = [[float(x.strip()) for x in line.split()] for line in response.text.splitlines()]

    flat_data = flatten_data(data)

    return flat_data

def fetch_aircraft_data():
    """
    Fetches and structures all 12 standard aircraft landing problem datasets.

    Returns:
        list: A list of AircraftLanding objects, each representing one dataset.
    """

    data = []
    for i in range(12):
        data.append(order_data(fetch_data(f"https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/airland{i+1}.txt")))
    return data