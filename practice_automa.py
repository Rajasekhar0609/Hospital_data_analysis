import pandas as pd
import numpy as np
import os

# =========================
# FILE PATHS
# =========================
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except:
    BASE_DIR = os.getcwd()

INPUT_FILE  = os.path.join(BASE_DIR, "hospital_messy_data_30k.csv")
CLEANED_FILE = os.path.join(BASE_DIR, "hospital_cleaned.csv")
SUMMARY_FILE = os.path.join(BASE_DIR, "hospital_summary.csv")

CHUNKSIZE = 25000

missing_tokens = ["", " ", "NA", "N/A", "na", "null", "NULL", "None", "none", "-", "abc"]

# =========================
# CLEANING FUNCTION
# =========================
def clean_chunk(chunk):

    chunk = chunk.replace(missing_tokens, np.nan)

    # TEXT CLEANING
    text_cols = [
        "patient_name", "gender", "city",
        "department", "doctor_name",
        "treatment_type", "payment_status",
        "admission_type"
    ]

    for col in text_cols:
        if col in chunk.columns:
            chunk[col] = chunk[col].astype("string").str.strip().str.title()

    # NUMERIC
    for col in ["age", "treatment_cost", "billing_amount", "insurance_coverage"]:
        if col in chunk.columns:
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce")

    # AGE FIX
    if "age" in chunk.columns:
        chunk.loc[(chunk["age"] <= 0) | (chunk["age"] > 120), "age"] = np.nan
        chunk["age_issue_flag"] = chunk["age"].isna()
        chunk["age"] = chunk["age"].fillna(0)

    # BILLING FIX
    if "billing_amount" in chunk.columns:
        chunk.loc[chunk["billing_amount"] <= 0, "billing_amount"] = np.nan
        chunk["billing_issue_flag"] = chunk["billing_amount"].isna()
        chunk["billing_amount"] = chunk["billing_amount"].fillna(0)

    # INSURANCE FIX
    if "insurance_coverage" in chunk.columns:
        chunk.loc[chunk["insurance_coverage"] < 0, "insurance_coverage"] = np.nan
        chunk["insurance_issue_flag"] = chunk["insurance_coverage"].isna()
        chunk["insurance_coverage"] = chunk["insurance_coverage"].fillna(0)

    if "length_of_stay" in chunk.columns:
        chunk.loc[chunk["length_of_stay"] < 0, "length_of_stay"] = np.nan
        chunk["length_of_stay"] = chunk["length_of_stay"].fillna(0)

    # MEDIAN FIX
    if "treatment_cost" in chunk.columns:
        med = chunk["treatment_cost"].median()
        if pd.isna(med):
            med = 0
        chunk["treatment_cost"] = chunk["treatment_cost"].fillna(med)

    # FILL TEXT
    for col in ["patient_name","doctor_name","treatment_type","city","department","payment_status","admission_type"]:
        if col in chunk.columns:
            chunk[col] = chunk[col].fillna("Unknown")

    # DATE SAFE CONVERSION
    if "admission_date" in chunk.columns:
        chunk["admission_date"] = pd.to_datetime(chunk["admission_date"], errors="coerce")

    if "discharge_date" in chunk.columns:
        chunk["discharge_date"] = pd.to_datetime(chunk["discharge_date"], errors="coerce")
###########################################
    # FEATURE ENGINEERING (SAFE) #
###########################################
    if "admission_date" in chunk.columns and "discharge_date" in chunk.columns:
        chunk["new_length_of_stay"] = (chunk["discharge_date"] - chunk["admission_date"]).dt.days
        if "new_length_of_stay" in chunk.columns:
            chunk.loc[chunk["new_length_of_stay"] < 0, "new_length_of_stay"] = np.nan
            chunk["new_length_of_stay"] = chunk["new_length_of_stay"].fillna(0)

    if "billing_amount" in chunk.columns and "insurance_coverage" in chunk.columns:
        chunk["new_insurance_amount"] = chunk["billing_amount"] * (chunk["insurance_coverage"] / 100)
        chunk["new_hospital_revenue"] = chunk["billing_amount"] - chunk["new_insurance_amount"]
        if "new_hospital_revenue" in chunk.columns:
            chunk.loc[chunk["new_hospital_revenue"] < 0, "new_hospital_revenue"] = np.nan
            chunk["new_hospital_revenue"] = chunk["new_hospital_revenue"].fillna(0)

    if "admission_date" in chunk.columns:
        chunk["admission_year"] = chunk["admission_date"].dt.year
        chunk["admission_month"] = chunk["admission_date"].dt.month


    chunk = chunk.sort_values(by="admission_date", ascending=False)
    chunk = chunk.drop_duplicates(subset="patient_id", keep="first")
    return chunk

# =========================
# REMOVE OLD FILES
# =========================
for file in [CLEANED_FILE, SUMMARY_FILE]:
    if os.path.exists(file):
        os.remove(file)

# =========================
# PROCESS
# =========================
summary_parts = []
first_write = True

for i, chunk in enumerate(pd.read_csv(INPUT_FILE, chunksize=CHUNKSIZE)):
    print(f"Processing chunk {i+1}")

    cleaned = clean_chunk(chunk)
    cleaned = cleaned.drop_duplicates()

    # SAVE CLEANED
    cleaned.to_csv(
        CLEANED_FILE,
        mode="w" if first_write else "a",
        header=first_write,
        index=False
    )
    first_write = False

    # =========================
    # SUMMARY (FIXED INSIDE LOOP)
    # =========================
    summary = cleaned.groupby(["department", "city"], dropna=False).agg(
        total_patients=("patient_name", "count"),
        total_revenue=("new_hospital_revenue", "sum"),
        avg_revenue=("new_hospital_revenue", "mean"),
        avg_stay=("new_length_of_stay", "mean"),
        age_issues=("age_issue_flag", "sum"),
        billing_issues=("billing_issue_flag", "sum"),
        insurance_issues=("insurance_issue_flag", "sum")
    ).reset_index()

    summary_parts.append(summary)

# =========================
# FINAL SUMMARY
# =========================
final_summary = pd.concat(summary_parts, ignore_index=True)

final_summary = final_summary.groupby(["department", "city"], dropna=False).agg(
    total_patients=("total_patients", "sum"),
    total_revenue=("total_revenue", "sum"),
    avg_revenue=("avg_revenue", "mean"),
    avg_stay=("avg_stay", "mean"),
    age_issues=("age_issues", "sum"),
    billing_issues=("billing_issues", "sum"),
    insurance_issues=("insurance_issues", "sum")
).reset_index()

final_summary.to_csv(SUMMARY_FILE, index=False)

print("\n✅ Cleaning Completed!")
print("Cleaned file:", CLEANED_FILE)
print("Summary file:", SUMMARY_FILE)

print("\n📊 ===== DATA ANALYSIS =====")

df = pd.read_csv(CLEANED_FILE)

# -------------------------
# Revenue by Department
# -------------------------
if "new_hospital_revenue" in df.columns:
    print("\n🔹 Revenue by Department")
    print(df.groupby("department")["new_hospital_revenue"].sum().sort_values(ascending=False))    

# -------------------------
# Avg Stay by Department
# -------------------------
if "new_length_of_stay" in df.columns:
    print("\n🔹 Avg Stay by Department")
    print(df.groupby("department")["new_length_of_stay"].mean().round(3))

# -------------------------
# Doctor Performance
# -------------------------
if "doctor_name" in df.columns:
    print("\n🔹 Doctor Performance")
    print(
        df.groupby("doctor_name").agg(
            total_revenue=("new_hospital_revenue", "sum"),
            total_patients=("patient_name", "count")
        ).sort_values("total_revenue", ascending=False)
    )

# -------------------------
# Patient Distribution
# -------------------------
if "city" in df.columns:
    print("\n🔹 Patient Distribution")
    print(df["city"].value_counts())

# -------------------------
# Admission Trends
# -------------------------
if "admission_year" in df.columns:
    print("\n🔹 Admission Trends")
    print(df.groupby(["admission_year", "admission_month"]).size())

