import json
import os
from datetime import datetime

class MachineProfile:
    def __init__(self, machine_id, machine_type, features):
        self.machine_id = machine_id
        self.machine_type = machine_type
        self.features = {
            'air_temp': float(features.get('air_temp', 0)),
            'process_temp': float(features.get('process_temp', 0)),
            'rotational_speed': float(features.get('rotational_speed', 0)),
            'torque': float(features.get('torque', 0)),
            'tool_wear': float(features.get('tool_wear', 0)),
            'failure': int(features.get('failure', 0))
        }
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_updated = self.created_at

    def save_to_file(self, directory="machine_profiles"):
        os.makedirs(directory, exist_ok=True)
        with open(f"{directory}/{self.machine_id}.json", "w") as f:
            json.dump(self.__dict__, f, indent=4)