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

# --- Grid Calculator ---
with st.expander("🧮 Calculator"):
    # Initialize calculator state
    if "calc_input" not in st.session_state:
        st.session_state.calc_input = ""

    def btn_click(val):
        st.session_state.calc_input += str(val)

    def calc_clear():
        st.session_state.calc_input = ""

    def calc_back():
        st.session_state.calc_input = st.session_state.calc_input[:-1]

    def calc_result():
        try:
            # Evaluate string as code (safe for simple math)
            st.session_state.calc_input = str(eval(st.session_state.calc_input))
        except:
            st.session_state.calc_input = "Error"

    # Display Screen
    st.text_input("Display", value=st.session_state.calc_input, label_visibility="collapsed", disabled=True)

    # Button Grid
    g1, g2, g3, g4 = st.columns(4)
    with g1: st.button("C", on_click=calc_clear, use_container_width=True)
    with g2: st.button("⌫", on_click=calc_back, use_container_width=True)
    with g3: st.button("%", on_click=btn_click, args=("/100",), use_container_width=True)
    with g4: st.button("÷", on_click=btn_click, args=("/",), use_container_width=True)

    g1, g2, g3, g4 = st.columns(4)
    with g1: st.button("7", on_click=btn_click, args=("7",), use_container_width=True)
    with g2: st.button("8", on_click=btn_click, args=("8",), use_container_width=True)
    with g3: st.button("9", on_click=btn_click, args=("9",), use_container_width=True)
    with g4: st.button("×", on_click=btn_click, args=("*",), use_container_width=True)

    g1, g2, g3, g4 = st.columns(4)
    with g1: st.button("4", on_click=btn_click, args=("4",), use_container_width=True)
    with g2: st.button("5", on_click=btn_click, args=("5",), use_container_width=True)
    with g3: st.button("6", on_click=btn_click, args=("6",), use_container_width=True)
    with g4: st.button("-", on_click=btn_click, args=("-",), use_container_width=True)

    g1, g2, g3, g4 = st.columns(4)
    with g1: st.button("1", on_click=btn_click, args=("1",), use_container_width=True)
    with g2: st.button("2", on_click=btn_click, args=("2",), use_container_width=True)
    with g3: st.button("3", on_click=btn_click, args=("3",), use_container_width=True)
    with g4: st.button("+", on_click=btn_click, args=("+",), use_container_width=True)
    
    g1, g2, g3, g4 = st.columns(4)
    with g1: st.button("00", on_click=btn_click, args=("00",), use_container_width=True)
    with g2: st.button("0", on_click=btn_click, args=("0",), use_container_width=True)
    with g3: st.button(".", on_click=btn_click, args=(".",), use_container_width=True)
    with g4: st.button("=", type="primary", on_click=calc_result, use_container_width=True)

# Input Form
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
            
            st.toast("Expense Added! Balance Updated.", icon="✅")
            st.rerun()
        else:
            st.error("Enter valid details")

st.divider()

# --- Tabs for Viewing Data ---
tab1, tab2 = st.tabs(["📉 Expenses (Edit/Delete)", "💰 Funds History"])

with tab1:
    st.subheader("Recent Expenses")
    st.info("📝 **To Edit:** Double-click any cell in the table below.\n\n🗑️ **To Delete:** You can use the specific delete tool below this table if you find it hard to delete rows directly.")
    
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

    # --- Explicit Delete Tool ---
    st.write("")
    with st.expander("🗑️ **Delete an Expense (Easier Way)**", expanded=False):
        if not df_expenses.empty:
            # Create a list of strings "Index | Date | Item | Amount" for the dropdown
            # We use the index 'i' to know exactly which row to delete
            delete_options = [f"{i} | {row['Date']} | {row['Item']} | ₹{row['Amount']}" for i, row in df_expenses.iterrows()]
            # Reverse so the newest ones are at the top
            delete_options.reverse()
            
            selected_to_delete = st.selectbox("Select the expense to delete:", delete_options)
            
            if st.button("Confirm Delete", type="primary"):
                if selected_to_delete:
                    # Extract the index (the number before the first " | ")
                    index_to_drop = int(selected_to_delete.split(" | ")[0])
                    
                    # Delete the row
                    df_expenses = df_expenses.drop(index_to_drop).reset_index(drop=True)
                    st.session_state.expenses = df_expenses
                    save_csv(df_expenses, EXPENSES_FILE)
                    
                    st.toast("Expense deleted successfully!", icon="🗑️")
                    st.rerun()
        else:
            st.write("No expenses to delete.")

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
