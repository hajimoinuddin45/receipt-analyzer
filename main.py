# main.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile

from backend.parser import process_file
from backend.database import init_db, insert_record, fetch_all_records
from backend.algorithms import compute_statistics, search_records, sort_records

# Setup
st.set_page_config(page_title="Receipt Analyzer", layout="wide")
st.title("📄 Receipt & Bill Analyzer")

# Initialize database
init_db()

# Upload Section
st.subheader("Upload Receipt or Bill")
uploaded_files = st.file_uploader("Upload files", type=['pdf', 'jpg', 'png', 'txt'], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
            tmp_file.write(file.read())
            tmp_file.flush()

            with open(tmp_file.name, 'r', encoding='utf-8') as debug_file:
                debug_text = debug_file.read()
                st.subheader(f"📂 Uploaded File Content: {file.name}")
                st.code(debug_text)

            with st.spinner(f"⏳ Processing {file.name}..."):
                parsed = process_file(tmp_file.name, file.name)
                if parsed:
                    # Create unique key for each file to avoid widget duplication
                    unique_key = f"{file.name}_{file.size}_{file.type}"

                    st.subheader(f"✏️ Review Parsed Fields for {file.name}")
                    vendor = st.text_input("Vendor", parsed['vendor'], key=f'vendor_{unique_key}')
                    date = st.text_input("Date (DD-MM-YYYY)", parsed['date'], key=f'date_{unique_key}')
                    amount = st.number_input("Amount", value=parsed['amount'], min_value=0.01, key=f'amount_{unique_key}')
                    category = st.text_input("Category", parsed['category'], key=f'category_{unique_key}')

                    if st.button(f"✅ Save '{file.name}'", key=f'save_{unique_key}'):
                        final_data = {
                            "vendor": vendor,
                            "date": date,
                            "amount": amount,
                            "category": category
                        }
                        insert_record(final_data)
                        st.success("✅ Record saved successfully!")

# Fetch & display records
st.subheader("Parsed Receipts")
records = fetch_all_records()
df = pd.DataFrame(records, columns=["ID", "Vendor", "Date", "Amount", "Category"])

if not df.empty:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
    df.dropna(subset=['Date'], inplace=True)

if df.empty:
    st.warning("📂 No receipt records found yet. Upload some to get started.")
else:
    st.dataframe(df)
    st.caption(f"📊 Showing {len(df)} records")

    # Download buttons
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", data=csv, file_name="receipts.csv", mime="text/csv")

    json_data = df.to_json(orient="records")
    st.download_button("📥 Download JSON", data=json_data, file_name="receipts.json", mime="application/json")

    # Search and Sort
    st.subheader("Search & Sort")
    col1, col2 = st.columns(2)

    with col1:
        query = st.text_input("🔎 Search by vendor")
        if query:
            df = search_records(df, query)

    with col2:
        sort_by = st.selectbox("↕️ Sort by", ["Vendor", "Date", "Amount"])
        df = sort_records(df, sort_by)

    st.dataframe(df)

    # Stats
    st.subheader("📈 Insights")
    stats = compute_statistics(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spend", f"₹{stats['total']:.2f}")
    col2.metric("Average Spend", f"₹{stats['mean']:.2f}")
    col3.metric("Top Vendor", stats['top_vendor'])

    # Visualizations
    st.subheader("📊 Visualizations")

    fig1, ax1 = plt.subplots()
    sns.countplot(data=df, x='Vendor', order=df['Vendor'].value_counts().index, ax=ax1)
    ax1.set_title("Vendor Frequency")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    df.groupby(df['Date'].dt.to_period('M')).sum(numeric_only=True)['Amount'].plot(kind='line', ax=ax2)
    ax2.set_title("Monthly Spend Trend")
    ax2.set_ylabel("Amount")
    st.pyplot(fig2)
