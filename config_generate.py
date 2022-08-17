import json

config = {
    "output_directory": "out",
    "categories": [1, 2, 3],
    "delay_range_s": {"min": 1, "max": 3},
    "max_retries": 3,
    "headers": {},
    "logs_dir": "main.log",
    "restart":
        {
            "restart_count": 3,
            "interval_m": 0.2
        }
    }

with open('config.json', 'w') as f:
    json.dump(config, f)
