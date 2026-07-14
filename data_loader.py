"""Load HR dashboard workbooks, normalize session data, and build derived tables."""
from __future__ import annotations

import io
import re
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

CARES_ORDER = ["Alignment", "Career", "Empowerment", "Recognition", "Strive"]
CARES_DESCRIPTIONS = {
    "Alignment": "Role and performance alignment with expectations.",
    "Career": "Career growth, development, and progression.",
    "Empowerment": "Enablement, autonomy, and confidence to act.",
    "Recognition": "Acknowledgement and reward for contributions.",
    "Strive": "Motivation, engagement, and aspiration.",
}
SENTIMENT_ORDER = ["Positive", "Neutral", "Mixed", "Negative"]
SEVERITY_ORDER = ["High", "Moderate", "Low"]
STATUS_ORDER = ["Open", "In-progress", "Closed"]

# Fuzzy matching patterns for mapping source workbook columns to target fields.
# If multiple columns match the same key, values will be consolidated dynamically.
FUZZY_PATTERNS = {
    "ID": [r"\bid\b", r"connect.*id", r"session.*id"],
    "date": [r"date.*connect", r"connect.*date", r"\bdate\b"],
    "associate_name": [r"\bname\b", r"associate.*name", r"employee.*name"],
    "bhr_name_canonical": [r"bhr.*name", r"name.*bhr", r"hrbp.*name", r"manager.*name"],
    "bhr_id": [r"bhr.*employee.*id", r"bhr.*id", r"id.*bhr", r"employee.*id"],
    "service_line": [r"service.*line", r"\bsl\b", r"line.*service"],
    "ibu_scope": [r"ibu.*scope", r"scope.*ibu", r"\bibu\b"],
    "engagement_type": [r"engagement.*type", r"type.*engagement"],
    "band": [r"\bband\b", r"\bgrade\b"],
    "cares_lever": [r"cares.*framework", r"cares.*lever", r"cares", r"framework"],
    "severity": [r"severity", r"priority"],
    "status": [r"status", r"stage"],
    "sentiment": [r"overall.*sentiment", r"sentiment", r"tone"],
    "engagement_mode": [r"engagement.*mode", r"mode.*engagement", r"connect.*mode", r"mode"],
    "cohort": [r"cohort", r"selected.*connect", r"connect.*name", r"connect.*type", r"engagement.*cohort"],
    "engagement_query": [r"queries", r"query", r"statement", r"comment", r"concern", r"question"],
    "action_owners": [r"action.*owner", r"owner.*action", r"assigned.*to", r"owners", r"owner"],
    "action_plan": [r"action.*plan", r"recommend", r"plan.*action", r"action"],
    "coverage_item": [r"coverage", r"item.*coverage", r"theme", r"insight", r"observation", r"comment", r"finding"],
}


def _find_best_row_value(row, target: str, default: str = "") -> str:
    """Extract a cell value from a row using fuzzy match on the column names."""
    import re
    if target == "ID":
        exact_id_col = None
        for col in row.index:
            if str(col).strip().lower() == "id":
                exact_id_col = col
                break
        if exact_id_col is not None:
            return _clean_string(row[exact_id_col])

        patterns = FUZZY_PATTERNS.get(target, [])
        for pat in patterns:
            for col in row.index:
                if re.search(pat, str(col), re.IGNORECASE):
                    if "employee" not in str(col).lower() and "bhr" not in str(col).lower():
                        val = _clean_string(row[col])
                        if val:
                            return val
        return default

    patterns = FUZZY_PATTERNS.get(target, [])
    # 1. Try pattern matching first
    for pat in patterns:
        for col in row.index:
            col_lower = str(col).lower()

            if target == "bhr_name_canonical":
                # Prevent accidental mapping of BHR numeric ID columns into BHR names
                if "id" in col_lower or "employee id" in col_lower or "emp id" in col_lower:
                    continue

            if target == "bhr_id":
                # Avoid pulling human-readable names into employee ID fields
                if "name" in col_lower:
                    continue

            if re.search(pat, str(col), re.IGNORECASE):
                val = _clean_string(row[col])
                if val:
                    return val
    # 2. Substring matching fallback
    target_norm = target.lower().replace("_", "")
    for col in row.index:
        col_norm = str(col).lower().replace(" ", "").replace("_", "").replace("-", "")
        if target_norm in col_norm:
            val = _clean_string(row[col])
            if val:
                return val
    return default


def _to_bytes_io(source):
    if isinstance(source, bytes):
        return io.BytesIO(source)
    if isinstance(source, io.BytesIO):
        return source
    return source


def _read_excel(source, sheet_name=None):
    source = _to_bytes_io(source)
    if isinstance(source, Path) and not source.exists():
        raise FileNotFoundError(source)
    return pd.read_excel(source, sheet_name=sheet_name, engine="openpyxl")


def _clean_string(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _normalize_bhr_name(name: str) -> str:
    cleaned = re.sub(r"\s+", " ", _clean_string(name))
    return cleaned.title() if cleaned else ""


def _first_nonempty(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    """Return the first non-empty value across the specified columns for each row."""
    result = pd.Series([""] * len(df), index=df.index)
    for col in reversed(columns):
        if col in df.columns:
            vals = df[col].astype(str).str.strip().replace({"nan": ""})
            result = result.where(result != "", vals)
    return result


def _normalize_sessions(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    out = pd.DataFrame(index=df.index)

    # Fuzzy find and populate each target column dynamically
    import re
    for target in FUZZY_PATTERNS.keys():
        if target in ("ID", "action_plan", "coverage_item"):
            continue
        matching_cols = []
        patterns = FUZZY_PATTERNS.get(target, [])
        for pat in patterns:
            for col in df.columns:
                if re.search(pat, str(col), re.IGNORECASE) and col not in matching_cols:
                    col_lower = str(col).lower()

                    if target == "associate_name" and "bhr" in col_lower:
                        continue

                    if target == "bhr_name_canonical":
                        # Exclude numeric employee ID columns from BHR name mapping
                        if "id" in col_lower or "employee id" in col_lower or "emp id" in col_lower:
                            continue

                    if target == "bhr_id":
                        # Exclude textual name columns from BHR employee ID mapping
                        if "name" in col_lower:
                            continue

                    matching_cols.append(col)
        # Substring match fallback
        target_norm = target.lower().replace("_", "")
        for col in df.columns:
            col_norm = str(col).lower().replace(" ", "").replace("_", "").replace("-", "")
            if target_norm in col_norm and col not in matching_cols:
                if target == "associate_name" and "bhr" in col_norm:
                    continue

                if target == "bhr_name_canonical":
                    if "id" in col_norm or "employeeid" in col_norm or "empid" in col_norm:
                        continue

                if target == "bhr_id":
                    if "name" in col_norm:
                        continue

                matching_cols.append(col)
        
        if matching_cols:
            out[target] = _first_nonempty(df, matching_cols)

    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="coerce")
    else:
        out["date"] = pd.NaT
    if out["date"].isna().all():
        out["date"] = pd.Series(pd.Timestamp.today(), index=df.index)

    text_cols = [
        "associate_name",
        "bhr_name_canonical",
        "bhr_id",
        "service_line",
        "ibu_scope",
        "engagement_type",
        "band",
        "cares_lever",
        "cohort",
        "severity",
        "status",
        "sentiment",
        "engagement_mode",
    ]

    for col in text_cols:
        if col in out.columns:
            out[col] = out[col].astype(str).str.strip().replace({"nan": ""})
        else:
            out[col] = ""

    if "bhr_name_canonical" in out.columns:
        out["bhr_name_canonical"] = out["bhr_name_canonical"].map(_normalize_bhr_name)

    for col in ("engagement_query", "action_owners"):
        if col in out.columns:
            out[col] = out[col].astype(str).replace({"nan": ""})
        else:
            out[col] = ""

    # Extract original Excel ID strictly
    exact_id_col = None
    for c in df.columns:
        if str(c).strip().lower() == "id":
            exact_id_col = c
            break
    if exact_id_col is not None:
        excel_id = df[exact_id_col]
    else:
        excel_id = pd.Series(dtype="Int64", index=df.index)
    try:
        out["excel_id"] = pd.to_numeric(excel_id, errors="coerce").astype("Int64")
    except Exception:
        out["excel_id"] = pd.Series(dtype="Int64", index=df.index)

    # Artificially assign unique sequential primary keys for all sessions
    out["ID"] = pd.Series(range(1, len(df) + 1), index=df.index, dtype="Int64")

    return out


def clean_active_bhr_count(sessions: pd.DataFrame) -> int:
    """Distinct BHRs after normalizing whitespace and casing."""
    if sessions is None or sessions.empty:
        return 0
    names = sessions["bhr_name_canonical"].replace({"": pd.NA}).dropna()
    normalized = names.map(_normalize_bhr_name).replace({"": pd.NA}).dropna()
    return normalized.nunique()

def _make_owners_long(sessions: pd.DataFrame) -> pd.DataFrame:
    if sessions is None or sessions.empty:
        return pd.DataFrame(columns=["ID", "owner"])

    records = []
    for _, row in sessions.iterrows():
        owners = _clean_string(row.get("action_owners", ""))
        if not owners:
            continue
        for owner in re.split(r"[;,]+", owners):
            owner = owner.strip()
            if owner:
                records.append({"ID": row.get("ID"), "owner": owner})
    if not records:
        return pd.DataFrame(columns=["ID", "owner"])
    return pd.DataFrame(records)


def _make_coverage_long(source_df: pd.DataFrame, sessions: pd.DataFrame) -> pd.DataFrame:
    if source_df is None or source_df.empty:
        return pd.DataFrame(columns=["ID", "coverage_item", "severity", "cares_lever"])

    coverage_columns = [
        c for c in source_df.columns
        if c.lower().startswith("coverage") or "coverage" in c.lower() or "theme" in c.lower()
    ]
    if not coverage_columns:
        import re
        patterns = FUZZY_PATTERNS.get("coverage_item", [])
        for pat in patterns:
            for c in source_df.columns:
                if re.search(pat, str(c), re.IGNORECASE) and c not in coverage_columns:
                    coverage_columns.append(c)

    # Build lookup mappings
    sessions_lookup = {}
    excel_id_lookup = {}
    if sessions is not None and not sessions.empty:
        for _, s_row in sessions.iterrows():
            bhr_emp_id = _clean_string(s_row.get("bhr_id", ""))
            date_val = s_row.get("date")
            date_str = date_val.strftime("%Y-%m-%d") if pd.notna(date_val) else ""
            bhr_name = _clean_string(s_row.get("bhr_name_canonical", "")).lower()
            
            # Map BHR + Date to a list of artificial IDs
            keys = []
            if bhr_emp_id and date_str:
                keys.append((bhr_emp_id, date_str))
            if bhr_name and date_str:
                keys.append((bhr_name, date_str))
            for k in keys:
                if k not in sessions_lookup:
                    sessions_lookup[k] = []
                sessions_lookup[k].append(s_row["ID"])
            
            # Map original Excel ID to a list of artificial IDs
            eid = s_row.get("excel_id")
            if pd.notna(eid):
                try:
                    eid_val = int(eid)
                    if eid_val not in excel_id_lookup:
                        excel_id_lookup[eid_val] = []
                    excel_id_lookup[eid_val].append(s_row["ID"])
                except Exception:
                    pass

    rows = []
    for i, (_, row) in enumerate(source_df.iterrows()):
        bhr_emp_id = _find_best_row_value(row, "bhr_id")
        bhr_name = _find_best_row_value(row, "bhr_name_canonical").lower()
        date_val = pd.to_datetime(_find_best_row_value(row, "date"), errors="coerce")
        date_str = date_val.strftime("%Y-%m-%d") if pd.notna(date_val) else ""
        
        matching_ids = []
        if bhr_emp_id and date_str and (bhr_emp_id, date_str) in sessions_lookup:
            matching_ids = sessions_lookup[(bhr_emp_id, date_str)]
        elif bhr_name and date_str and (bhr_name, date_str) in sessions_lookup:
            matching_ids = sessions_lookup[(bhr_name, date_str)]
        else:
            raw_eid = _find_best_row_value(row, "ID")
            try:
                raw_eid = int(float(raw_eid)) if raw_eid else None
            except Exception:
                raw_eid = None
            if raw_eid is not None and raw_eid in excel_id_lookup:
                matching_ids = excel_id_lookup[raw_eid]
            else:
                # Absolute fallback: map to sequential row index
                matching_ids = [i + 1]

        for row_id in matching_ids:
            for col in coverage_columns:
                item = _clean_string(row.get(col, ""))
                if item:
                    rows.append(
                        {
                            "ID": row_id,
                            "coverage_item": item,
                            "severity": _find_best_row_value(row, "severity"),
                        }
                    )
    coverage = pd.DataFrame(rows)
    if coverage.empty or sessions is None or sessions.empty:
        return pd.DataFrame(columns=["ID", "coverage_item", "severity", "cares_lever"])

    session_meta = sessions[["ID", "cares_lever", "severity"]].drop_duplicates("ID").copy()
    session_meta = session_meta.rename(columns={"severity": "session_severity"})
    coverage = coverage.merge(session_meta, on="ID", how="left")
    coverage["severity"] = coverage["severity"].replace({"": pd.NA}).fillna(coverage.get("session_severity", ""))
    coverage["cares_lever"] = coverage["cares_lever"].fillna("Unspecified")
    coverage = coverage.drop(columns=["session_severity"], errors="ignore")
    return coverage


def _make_library_from_insight(df: pd.DataFrame) -> tuple[dict, dict]:
    lever_library: dict = {}
    cohort_library: dict = {}

    if df is None or df.empty:
        return lever_library, cohort_library

    for _, row in df.iterrows():
        lever = _find_best_row_value(row, "cares_lever") or "Unspecified"
        cohort = (
            _find_best_row_value(row, "cohort")
            or _find_best_row_value(row, "engagement_type")
            or "Unspecified"
        )
        insight = (
            _find_best_row_value(row, "engagement_query")
            or _find_best_row_value(row, "coverage_item")
            or "Insight not available"
        )
        action = _find_best_row_value(row, "action_plan") or "Not specified"
        description = _find_best_row_value(row, "description") or ""

        lever_area = cohort if cohort else "General"
        lever_library.setdefault(lever, {}).setdefault(lever_area, []).append(
            {"insight": insight, "action": action}
        )

        cohort_library.setdefault(lever, {}).setdefault(cohort, []).append(
            {
                "insight": insight,
                "description": description,
                "action": action,
            }
        )

    return lever_library, cohort_library


def _finalize_demo_sessions(df: pd.DataFrame) -> pd.DataFrame:
    """Lightweight finalizer for demo DataFrames that already use internal column names."""
    df = df.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    text_cols = [
        "associate_name", "bhr_name_canonical", "bhr_id", "service_line", "ibu_scope",
        "engagement_type", "band", "cares_lever", "cohort",
        "severity", "status", "sentiment", "engagement_mode",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"nan": ""})
    if "bhr_name_canonical" in df.columns:
        df["bhr_name_canonical"] = df["bhr_name_canonical"].map(_normalize_bhr_name)
    for col in ("engagement_query", "action_owners"):
        if col in df.columns:
            df[col] = df[col].astype(str).replace({"nan": ""})
    if "ID" in df.columns:
        try:
            df["ID"] = pd.to_numeric(df["ID"], errors="coerce").astype("Int64")
        except Exception:
            pass
    return df


# Realistic fictional BHR names for the demo dataset
_DEMO_BHR_NAMES = [
    "Arjun Mehta", "Priya Sharma", "Rahul Nair", "Ananya Iyer", "Vikram Patel",
    "Sneha Reddy", "Karthik Bose", "Divya Krishnan", "Amit Joshi", "Neha Gupta",
    "Suresh Pillai", "Lakshmi Venkat", "Rohit Choudhary", "Deepa Menon", "Sanjay Kapoor",
    "Meera Nambiar", "Ajay Tiwari", "Kavya Rao", "Nikhil Saxena", "Pooja Agarwal",
    "Harish Kumar", "Swati Bhatt", "Ravi Shankar", "Aarti Singh", "Manish Deshpande",
    "Shilpa Varma", "Gaurav Malhotra", "Rekha Pillai", "Tarun Jain", "Sunita Nair",
]


def _build_demo_dataset() -> SimpleNamespace:
    """Synthetic workbook data so the app runs without bundled Excel files."""
    import numpy as np

    rng = np.random.default_rng(42)
    n = 96
    dates = pd.date_range(end=pd.Timestamp.today(), periods=n, freq="3D")
    service_lines = ["BFSI", "Healthcare", "Retail", "Manufacturing", "Telecom"]
    cohorts = ["Monthly Connect", "Quarterly Review", "Skip-level", "Pulse Check"]
    modes = ["Virtual", "In-person", "Hybrid"]
    owners = ["Priya Sharma", "Raj Mehta", "Anita Desai", "Vikram Rao", "Neha Patel"]
    coverage_pool = [
        "Career progression clarity",
        "Workload balance",
        "Recognition frequency",
        "Role clarity",
        "Learning opportunities",
        "Manager accessibility",
        "Team collaboration",
        "Compensation transparency",
        "Well-being support",
        "Process bottlenecks",
    ]
    queries = [
        "Associate flagged unclear growth path for the next review cycle.",
        "Team raised concerns about after-hours workload during release weeks.",
        "Positive feedback on recent recognition, but wants more peer visibility.",
        "Requested clearer OKRs and mid-quarter check-ins from leadership.",
        "Asked for structured upskilling budget and mentor pairing.",
    ]

    # Use realistic names — each session uniquely assigns a BHR from the pool
    bhr_names = [_DEMO_BHR_NAMES[i % len(_DEMO_BHR_NAMES)] for i in range(n)]

    sessions = pd.DataFrame(
        {
            "ID": range(1, n + 1),
            "date": dates,
            "associate_name": [f"Associate-{100 + i}" for i in range(n)],
            "bhr_name_canonical": bhr_names,
            "bhr_id": [f"BHR-{1000 + i}" for i in range(n)],
            "service_line": rng.choice(service_lines, n),
            "ibu_scope": rng.choice(["India", "Americas", "EMEA", "APAC"], n),
            "engagement_type": rng.choice(["Structured", "Ad-hoc"], n),
            "band": rng.choice(["B4", "B5", "B6", "B7"], n),
            "cares_lever": rng.choice(CARES_ORDER, n),
            "cohort": rng.choice(cohorts, n),
            "severity": rng.choice(SEVERITY_ORDER, n, p=[0.22, 0.38, 0.40]),
            "status": rng.choice(STATUS_ORDER, n, p=[0.28, 0.34, 0.38]),
            "sentiment": rng.choice(SENTIMENT_ORDER, n, p=[0.35, 0.25, 0.22, 0.18]),
            "engagement_mode": rng.choice(modes, n),
            "engagement_query": rng.choice(queries, n),
            "action_owners": [", ".join(rng.choice(owners, 2, replace=False)) for _ in range(n)],
        }
    )

    insight_rows = []
    for _, row in sessions.iterrows():
        picks = rng.choice(coverage_pool, rng.integers(1, 4), replace=False)
        insight_rows.append(
            {
                "ID": row["ID"],
                "Coverage": picks[0],
                "Coverage 2": picks[1] if len(picks) > 1 else "",
                "Severity": row["severity"],
                "CARES Framework": row["cares_lever"],
                "Selected Connect": row["cohort"],
                "Description": f"Recurring theme under {row['cares_lever']}.",
                "Action Plan": "Schedule follow-up with HRBP and track closure in 2 weeks.",
            }
        )
    insight_df = pd.DataFrame(insight_rows)

    library_rows = []
    for lever in CARES_ORDER:
        for cohort in cohorts[:3]:
            library_rows.append(
                {
                    "CARES Framework": lever,
                    "Selected Connect": cohort,
                    "Coverage": f"{lever} signal: {coverage_pool[len(library_rows) % len(coverage_pool)]}",
                    "Description": CARES_DESCRIPTIONS[lever],
                    "Action Plan": "Review with service-line HR lead and update playbook.",
                }
            )
    library_df = pd.DataFrame(library_rows)

    # Demo DataFrame already uses internal column names — skip source-column remapping,
    # only apply text cleanup and date coercion.
    sessions = _finalize_demo_sessions(sessions)
    owners_long = _make_owners_long(sessions)
    coverage_long = _make_coverage_long(insight_df, sessions)
    lever_library, cohort_library = _make_library_from_insight(library_df)

    return SimpleNamespace(
        sessions=sessions,
        owners_long=owners_long,
        coverage_long=coverage_long,
        lever_library=lever_library,
        cohort_library=cohort_library,
        warnings=[
            "Bundled workbooks not found — showing a synthetic demo dataset. "
            "Upload HR_Dashboard_Final.xlsx and Engagement_Library.xlsx in the sidebar to load live data."
        ],
        is_demo=True,
    )


def load_dataset(dashboard_source, library_source):
    warnings: list[str] = []
    error: str | None = None
    dashboard_df = None
    insight_df = None

    if isinstance(dashboard_source, (str, Path)) and not Path(dashboard_source).exists():
        return _build_demo_dataset()

    lib_missing = isinstance(library_source, (str, Path)) and not Path(library_source).exists()

    try:
        dashboard_df = _read_excel(dashboard_source, sheet_name="Data_Summary")
    except FileNotFoundError:
        return _build_demo_dataset()
    except Exception as e1:
        try:
            dashboard_df = _read_excel(dashboard_source, sheet_name="Data")
            warnings.append("Data_Summary sheet not found; loaded Data sheet instead.")
        except FileNotFoundError:
            return _build_demo_dataset()
        except Exception as exc:
            error_msg = str(exc)
            if "permission" in error_msg.lower() or "denied" in error_msg.lower() or "sharing violation" in error_msg.lower():
                error = "The Excel file is currently open in Excel or locked. Please close Excel and try again."
            else:
                error = f"Unable to load dashboard workbook: {exc}"
            warnings.append(error)
            demo = _build_demo_dataset()
            demo.error = error
            demo.warnings = warnings + demo.warnings
            return demo

    try:
        insight_df = _read_excel(dashboard_source, sheet_name="Data_Insight")
    except Exception:
        insight_df = None

    library_df = None
    if library_source is not None and not lib_missing:
        try:
            library_df = _read_excel(library_source)
        except Exception:
            warnings.append(
                "Unable to load engagement library workbook; library content will be synthesized from the dashboard."
            )
    elif lib_missing:
        warnings.append(
            "Engagement library workbook not found; library content will be synthesized from the dashboard."
        )

    sessions = _normalize_sessions(dashboard_df)
    if sessions.empty:
        error = "The loaded Excel workbook is empty or does not match the expected column structure."
        demo = _build_demo_dataset()
        demo.error = error
        demo.warnings.append(error)
        return demo

    owners_long = _make_owners_long(sessions)
    coverage_long = _make_coverage_long(insight_df if insight_df is not None else dashboard_df, sessions)

    if library_df is not None:
        lever_library, cohort_library = _make_library_from_insight(library_df)
    else:
        lever_library, cohort_library = _make_library_from_insight(
            insight_df if insight_df is not None else dashboard_df
        )

    return SimpleNamespace(
        sessions=sessions,
        owners_long=owners_long,
        coverage_long=coverage_long,
        lever_library=lever_library,
        cohort_library=cohort_library,
        warnings=warnings,
        is_demo=False,
        error=None,
    )
