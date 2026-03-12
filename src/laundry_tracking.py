import time
import requests

SCHOOL_DESC_KEY = "7"
ROOM_LIST_URL = "https://www.laundryview.com/api/c_room"
ROOM_DATA_URL = "https://www.laundryview.com/api/currentRoomData"

# 10 floor laundry locations chosen from Northeastern rooms list
SELECTED_FLOORS = [
    ("1343669", "HASTINGS HALL - 7TH FLOOR"),
    ("13436071", "HASTINGS HALL- 3RD FLOOR"),
    ("134369", "KERR HALL 3RD FLOOR"),
    ("1343646", "KERR HALL 4TH FLOOR"),
    ("1343647", "KERR HALL 5TH FLOOR"),
    ("1343648", "KERR HALL 6TH FLOOR"),
    ("1343654", "SMITH HALL 1ST FLOOR"),
    ("1343655", "SMITH HALL 2ND FLOOR"),
    ("1343652", "WEST VILLAGE F 3RD FLOOR"),
    ("1343653", "WEST VILLAGE F 5TH FLOOR"),
]


def is_machine(obj: dict) -> bool:
    return bool(obj.get("appliance_desc_key")) and obj.get("appliance_type") in {"W", "D"}


def count_open_closed(objects: list[dict]) -> dict:
    machines = [obj for obj in objects if is_machine(obj)]

    washers = [obj for obj in machines if obj.get("appliance_type") == "W"]
    dryers = [obj for obj in machines if obj.get("appliance_type") == "D"]

    # LaundryView uses status_toggle == 0 for available/open in list view logic.
    washers_open = sum(1 for obj in washers if obj.get("status_toggle") == 0)
    dryers_open = sum(1 for obj in dryers if obj.get("status_toggle") == 0)

    return {
        "total": len(machines),
        "open": washers_open + dryers_open,
        "closed": len(machines) - (washers_open + dryers_open),
        "washers_open": washers_open,
        "washers_closed": len(washers) - washers_open,
        "dryers_open": dryers_open,
        "dryers_closed": len(dryers) - dryers_open,
    }


def get_room_data(session: requests.Session, location_id: str) -> dict:
    params = {
        "school_desc_key": SCHOOL_DESC_KEY,
        "location": location_id,
        "rdm": str(int(time.time() * 1000)),
    }
    response = session.get(ROOM_DATA_URL, params=params, timeout=(10, 20))
    response.raise_for_status()
    return response.json()


def validate_selected_locations(session: requests.Session) -> dict[str, str]:
    params = {
        "cui": "1",
        "loc": SCHOOL_DESC_KEY,
        "rdm": str(int(time.time() * 1000)),
    }
    response = session.get(ROOM_LIST_URL, params=params, timeout=(10, 20))
    response.raise_for_status()
    data = response.json()

    available = {}
    for item in data.get("room_data", []):
        loc = str(item.get("laundry_room_location", ""))
        name = item.get("laundry_room_name", "")
        if loc:
            available[loc] = name
    return available


def main() -> None:
    session = requests.Session()
    session.headers.update({"User-Agent": "laundry-status/1.0"})

    print("Checking selected floor locations...")
    available_locations = validate_selected_locations(session)
    print()

    print("Open/Closed laundry machine counts (10 selected floors):")
    print("-" * 92)
    print(
        f"{'Floor':45} {'Open':>5} {'Closed':>7} {'W(Open/Closed)':>16} {'D(Open/Closed)':>16}"
    )
    print("-" * 92)

    for location_id, fallback_name in SELECTED_FLOORS:
        floor_name = available_locations.get(location_id, fallback_name)
        try:
            room_data = get_room_data(session, location_id)
            counts = count_open_closed(room_data.get("objects", []))

            print(
                f"{floor_name[:45]:45} "
                f"{counts['open']:>5} "
                f"{counts['closed']:>7} "
                f"{counts['washers_open']}/{counts['washers_closed']:>11} "
                f"{counts['dryers_open']}/{counts['dryers_closed']:>11}"
            )
        except Exception as err:
            print(f"{floor_name[:45]:45} ERROR   ({err})")

    print("-" * 92)


if __name__ == "__main__":
    main()
