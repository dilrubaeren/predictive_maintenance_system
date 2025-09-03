import os
import sys
import tkinter as tk
from pathlib import Path
from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer
from src.app_interface import PredictiveMaintenanceApp

def initialize():
    paths = ["data", "machine_profiles", "models/trained_models/classification"]
    for path in paths:
        os.makedirs(path, exist_ok=True)

def run_data_processing():
    processor = DataProcessor()
    processor.process_data()

def run_model_training():
    trainer = ModelTrainer()
    trainer.train_all()

def start_gui():
    root = tk.Tk()
    PredictiveMaintenanceApp(root)
    root.mainloop()

if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent
    sys.path.append(str(BASE_DIR))
    initialize()
    run_data_processing()
    run_model_training()
    start_gui()