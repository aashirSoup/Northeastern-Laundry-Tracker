# Northeastern-Laundry-Tracker

This script checks LaundryView for 10 selected Northeastern residence hall floors and shows how many laundry machines are open vs closed on each floor.

It prints a table with:

- Floor name
- Open machines
- Closed machines
- Washer open/closed count
- Dryer open/closed count

## Requirements

- Python 3.9+
- `requests`

## How to run

From this project folder:

1. Install dependency:

```bash
pip install requests
```

2. Run the tracker:

```bash
python src/laundry_testing_ev2.py
```

The script will fetch live data from LaundryView and print the current counts.
