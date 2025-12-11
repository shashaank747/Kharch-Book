import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Configuration ---
st.set_page_config(page_title="Kharch Book", page_icon="💰", layout="centered")
FILE_PATH = 'expenses.csv'

# --- Helper Functions ---
def load_data():
    """Loads expenses from CSV or creates a new DataFrame."""
    if os.path.exists(FILE_PATH):
        try:
            return pd.read_csv(FILE_PATH)
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame(columns=["Date", "Item", "Category", "Amount"])
    else:
        return pd.DataFrame(columns=["Date", "Item", "Category", "Amount"])

def save_data(df):
    """Saves the DataFrame to a CSV file."""
    df.to_csv(FILE_PATH, index=False)

# --- App Logic ---
st.title("💰 Kharch Book")
st.caption("Your personal expense tracker.")

# 1. Load Data
if 'expenses' not in st.session_state:
    st.session_state.expenses = load_data()

df = st.session_state.expenses

# 2. Month End Reminder
today = datetime.now()
if today.day > 25:
    st.warning("⚠️ **Month End Reminder:** It's late in the month! Please download your CSV backup below to ensure your data is safe.", icon="📅")

# 3. Input Form
with st.container(border=True):
    st.subheader("Add New Expense")
    col1, col2 = st.columns(2)
    
    with col1:
        item = st.text_input("Description", placeholder="e.g. Vegetables, Auto")
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
    
    with col2:
        category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Other"])
        date = st.date_input("Date", datetime.now())

    if st.button("Add Expense", type="primary", use_container_width=True):
        if item and amount > 0:
            new_entry = pd.DataFrame([{
                "Date": date.strftime("%Y-%m-%d"),
                "Item": item,
                "Category": category,
                "Amount": amount
            }])
            # Add to top of list (concat new + old)
            df = pd.concat([new_entry, df], ignore_index=True)
            st.session_state.expenses = df
            save_data(df)
            st.toast("Expense added successfully!", icon="✅")
            st.rerun()
        else:
            st.error("Please enter a valid description and amount.")

# 4. Dashboard Metrics
if not df.empty:
    st.divider()
    
    # Calculate totals
    total_spent = df['Amount'].sum()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_spent = df[df['Date'] == today_str]['Amount'].sum()

    m1, m2 = st.columns(2)
    m1.metric("Spent Today", f"₹{today_spent:,.2f}")
    m2.metric("Total Spent", f"₹{total_spent:,.2f}")

    # 5. Data Editor (View & Delete)
    st.subheader("Recent Activity")
    st.caption("You can edit details or delete rows directly in the table below.")
    
    edited_df = st.data_editor(
        df,
        num_rows="dynamic", # Allows adding/deleting rows
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount": st.column_config.NumberColumn(format="₹%.2f"),
            "Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "Category": st.column_config.SelectboxColumn(
                options=["Food", "Travel", "Bills", "Shopping", "Other"]
            )
        }
    )

    # Save changes if user edits the table directly
    if not edited_df.equals(df):
        st.session_state.expenses = edited_df
        save_data(edited_df)
        st.rerun()

    # 6. Export Button
    st.divider()
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Expenses (CSV)",
        data=csv_data,
        file_name=f'kharch_book_{datetime.now().strftime("%Y-%m-%d")}.csv',
        mime='text/csv',
        use_container_width=True,
        help="Click this to save a backup of your expenses to your device."
    )

else:
    st.info("No expenses found. Add your first expense above!")
