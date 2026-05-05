# 🏥 Hospital Data Analysis Project

## 📌 Project Overview
This project simulates a real-world healthcare analytics scenario where raw hospital data is transformed into meaningful business insights.

The dataset contains **30,000+ hospital records** with multiple issues such as missing values, inconsistencies, and invalid entries. A complete data cleaning and analysis pipeline was built using Python.

---

## 🎯 Objective
- Clean messy healthcare data  
- Perform feature engineering  
- Analyze hospital performance  
- Generate actionable business insights  

---

## 🛠️ Tech Stack
- Python (Pandas, NumPy)  
- Excel  
- SQL  
- Power BI  

---

## 📂 Project Structure
hospital-data-analysis/
│── hospital_messy_data_30k.csv # Raw dataset
│── hospital_cleaned.csv # Cleaned dataset
│── hospital_summary.csv # Summary data
│── data_cleaning.py # Python script
│── README.md # Documentation


---

## 🔍 Data Cleaning Steps
- Handled missing values without dropping rows  
- Standardized text columns (city, department, doctor)  
- Fixed invalid values (age, billing, insurance)  
- Converted date columns to datetime format  
- Removed duplicate records  

---

## ⚙️ Feature Engineering
- Created **Length of Stay**  
- Calculated **Insurance Amount**  
- Derived **Hospital Revenue**  
- Extracted **Month & Year from dates**  

---

## 📊 Analysis Performed
- Revenue by Department  
- Average Stay by Department  
- Doctor Performance  
- Patient Distribution by City  
- Monthly Admission Trends  

---

## 💡 Key Insights
- Revenue is evenly distributed across departments (~198M–204M)  
- Orthopedics & Cardiology have highest patient stay (~14 days)  
- Large number of records have missing doctor information  
- “Unknown” city has highest patient count  
- Admission trends are stable across months  

---

## 📈 Business Recommendations
- Improve discharge planning to reduce patient stay  
- Make doctor assignment mandatory  
- Improve data collection during registration  
- Use location data for better decision-making  

---

## 🚀 How to Run
1. Clone the repository
