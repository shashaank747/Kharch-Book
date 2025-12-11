import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Configuration ---
st.set_page_config(page_title="Kharch Book", page_icon="💰", layout="wide")
EXPENSES_FILE = 'expenses.csv'
FUNDS_FILE = 'funds.csv'

# --- Helper Functions ---
def load_csv(file_path, columns):
    """Loads CSV or creates new DataFrame with specific columns."""
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Fix dates
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
            # Migration: Add missing columns if they don't exist (for old files)
            for col in columns:
                if col not in df.columns:
                    df[col] = "Online" if col == "Mode" else ""
            return df
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")
            return pd.DataFrame(columns=columns)
    else:
        return pd.DataFrame(columns=columns)

def save_csv(df, file_path):
    df.to_csv(file_path, index=False)

# --- App Logic ---
st.title("💰 Kharch Book")

# 1. Load Data
if 'expenses' not in st.session_state:
    st.session_state.expenses = load_csv(EXPENSES_FILE, ["Date", "Item", "Category", "Amount", "Mode"])
if 'funds' not in st.session_state:
    st.session_state.funds = load_csv(FUNDS_FILE, ["Date", "Source", "Mode", "Amount"])

df_expenses = st.session_state.expenses
df_funds = st.session_state.funds

# --- Sidebar: Wallet Management ---
with st.sidebar:
    st.header("💳 Wallet Setup")
    st.caption("Enter the total money you have (Opening Balance) or add money when you receive salary/withdraw cash.")
    
    with st.form("add_funds_form"):
        f_amount = st.number_input("Amount to Add (₹)", min_value=0.0, step=100.0)
        f_mode = st.radio("Wallet", ["Online (UPI/Bank)", "Cash"], horizontal=True)
        f_source = st.text_input("Source Note", placeholder="e.g. Salary, ATM Withdrawl")
        
        if st.form_submit_button("Add to Wallet"):
            if f_amount > 0:
                new_fund = pd.DataFrame([{
                    "Date": datetime.now().date(),
                    "Source": f_source if f_source else "Manual Add",
                    "Mode": "Online" if "Online" in f_mode else "Cash",
                    "Amount": f_amount
                }])
                df_funds = pd.concat([new_fund, df_funds], ignore_index=True)
                st.session_state.funds = df_funds
                save_csv(df_funds, FUNDS_FILE)
                st.success("Funds added!")
                st.rerun()

    st.divider()
    
    # Calculate Balances
    # 1. Total In (Funds)
    total_cash_in = df_funds[df_funds['Mode'] == 'Cash']['Amount'].sum()
    total_online_in = df_funds[df_funds['Mode'] == 'Online']['Amount'].sum()
    
    # 2. Total Out (Expenses)
    # Handle legacy data where 'Mode' might be missing or mixed
    if 'Mode' in df_expenses.columns:
        total_cash_out = df_expenses[df_expenses['Mode'] == 'Cash']['Amount'].sum()
        total_online_out = df_expenses[df_expenses['Mode'] != 'Cash']['Amount'].sum() # Default non-cash to online
    else:
        total_cash_out = 0
        total_online_out = df_expenses['Amount'].sum()

    # 3. Net Balance
    bal_cash = total_cash_in - total_cash_out
    bal_online = total_online_in - total_online_out

    st.metric("💵 Cash Balance", f"₹{bal_cash:,.2f}")
    st.metric("📱 Online Balance", f"₹{bal_online:,.2f}")
    
    if bal_cash < 0 or bal_online < 0:
        st.error("Warning: Negative balance detected! Did you forget to add some initial funds?")

# --- Main Page: Expense Entry ---

# Month End Reminder
if datetime.now().day > 25:
    st.warning("⚠️ **Month End:** Remember to download your data backup!", icon="📅")

# Calculator
with st.expander("🧮 Quick Calculator"):
    c1, c2, c3 = st.columns([1, 0.5, 1])
    n1 = c1.number_input("N1", 0.0, step=10.0, key="n1")
    op = c2.selectbox("Op", ["+", "-", "*", "/"], key="op")
    n2 = c3.number_input("N2", 0.0, step=10.0, key="n2")
    res = 0
    if op == "+": res = n1 + n2
    elif op == "-": res = n1 - n2
    elif op == "*": res = n1 * n2
    elif op == "/" and n2 != 0: res = n1 / n2
    st.caption(f"Result: **{res}**")

# Input Form
# FIX: Using st.form with clear_on_submit=True prevents the Session State error
with st.form("add_expense_form", clear_on_submit=True, border=True):
    st.subheader("Add New Expense")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        item = st.text_input("Description", placeholder="e.g. Burger, Uber", key="item_in")
        category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Other"], key="cat_in")
    
    with col2:
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, key="amt_in")
        date = st.date_input("Date", datetime.now())
        
    with col3:
        st.write("Paid Via:")
        mode = st.radio("Mode", ["Online", "Cash"], key="mode_in")
        
    # Form submit button
    submitted = st.form_submit_button("Add Expense", type="primary", use_container_width=True)
    
    if submitted:
        if item and amount > 0:
            new_entry = pd.DataFrame([{
                "Date": date,
                "Item": item,
                "Category": category,
                "Amount": amount,
                "Mode": mode
            }])
            # Append directly to session state
            st.session_state.expenses = pd.concat([new_entry, st.session_state.expenses], ignore_index=True)
            save_csv(st.session_state.expenses, EXPENSES_FILE)
            
            # Note: We do NOT need to manually clear inputs here. 
            # clear_on_submit=True handles it automatically.
            
            st.toast("Expense Added! Balance Updated.", icon="✅")
            st.rerun()
        else:
            st.error("Enter valid details")

st.divider()

# --- Tabs for Viewing Data ---
tab1, tab2 = st.tabs(["📉 Expenses (Edit/Delete)", "💰 Funds History"])

with tab1:
    st.subheader("Recent Expenses")
    st.caption("You can edit details or delete rows below. **Balances update automatically.**")
    
    edited_expenses = st.data_editor(
        df_expenses,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount": st.column_config.NumberColumn(format="₹%.2f"),
            "Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "Mode": st.column_config.SelectboxColumn(options=["Online", "Cash"], required=True)
        }
    )
    
    if not edited_expenses.equals(df_expenses):
        st.session_state.expenses = edited_expenses
        save_csv(edited_expenses, EXPENSES_FILE)
        st.rerun()

with tab2:
    st.subheader("Funds Log")
    st.caption("History of money added to wallet.")
    
    edited_funds = st.data_editor(
        df_funds,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="funds_editor",
        column_config={
            "Amount": st.column_config.NumberColumn(format="₹%.2f"),
            "Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "Mode": st.column_config.SelectboxColumn(options=["Online", "Cash"])
        }
    )
    
    if not edited_funds.equals(df_funds):
        st.session_state.funds = edited_funds
        save_csv(edited_funds, FUNDS_FILE)
        st.rerun()

# Export
st.divider()
csv = df_expenses.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Expenses CSV", csv, "expenses.csv", "text/csv")
