# backend/algorithms.py
import pandas as pd
from typing import Any, Dict


def search_records(df: pd.DataFrame, query: str) -> pd.DataFrame:
    return df[df['Vendor'].str.contains(query, case=False, na=False)]


def sort_records(df: pd.DataFrame, sort_by: str) -> pd.DataFrame:
    if sort_by == "Amount":
        return df.sort_values(by="Amount", ascending=False)
    elif sort_by == "Date":
        return df.sort_values(by="Date", ascending=False)
    else:
        return df.sort_values(by="Vendor")


def compute_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    stats = {
        "total": df["Amount"].sum(),
        "mean": df["Amount"].mean() if not df.empty else 0,
        "top_vendor": df["Vendor"].mode().iloc[0] if not df.empty else "N/A",
    }
    return stats
