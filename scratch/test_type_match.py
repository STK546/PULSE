import pandas as pd
from app import get_dataset_v4, enrich_sessions_v2
import os

DEFAULT_DASHBOARD = "HR_Dashboard_Final.xlsx"

if os.path.exists(DEFAULT_DASHBOARD):
    dataset = get_dataset_v4(None, None)
    sessions_raw = dataset.sessions
    
    max_date = sessions_raw["date"].max()
    as_of = max_date if pd.notna(max_date) else pd.Timestamp.today()
    sessions_all = enrich_sessions_v2(sessions_raw, str(as_of))
    
    sessions = sessions_all.copy() # no filters applied
    
    print("sessions ID dtype:", sessions["ID"].dtype)
    print("coverage_long ID dtype:", dataset.coverage_long["ID"].dtype)
    
    cov = dataset.coverage_long.merge(sessions[["ID"]], on="ID", how="inner")
    print("Merge result shape:", cov.shape)
else:
    print("Not found")
