from app import get_dataset_v5
import os

DEFAULT_DASHBOARD = "HR_Dashboard_Final.xlsx"

if os.path.exists(DEFAULT_DASHBOARD):
    dataset = get_dataset_v5(None, None)
    print("get_dataset_v5 sessions columns:", list(dataset.sessions.columns))
else:
    print("Not found")
