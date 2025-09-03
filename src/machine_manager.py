import os
import json
from src.machine_profile import MachineProfile

class MachineManager:
    def __init__(self):
        self.machines = {}
        self.load_profiles()

    def load_profiles(self):
        if not os.path.exists("machine_profiles"):
            return
        for filename in os.listdir("machine_profiles"):
            if filename.endswith(".json"):
                with open(f"machine_profiles/{filename}", "r") as f:
                    data = json.load(f)
                    machine = MachineProfile(
                        data['machine_id'],
                        data['machine_type'],
                        data['features']
                    )
                    self.machines[machine.machine_id] = machine

    def create_machine(self, machine_id, machine_type, features):
        if machine_id in self.machines:
            print(f"⚠️ Uyarı: {machine_id} zaten var! Üzerine yazılıyor...")
        new_machine = MachineProfile(machine_id, machine_type, features)
        self.machines[machine_id] = new_machine
        new_machine.save_to_file()
        return new_machine