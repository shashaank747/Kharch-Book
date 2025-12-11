import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import os

# --- Configuration ---
st.set_page_config(page_title="Kharch Book", page_icon="💰", layout="wide", initial_sidebar_state="collapsed")

# --- Custom CSS for Mobile UI Polish ---
st.markdown("""
<style>
    /* Main Background adjustments */
    .stApp {
        background-color: #000000;
    }
    
    /* We DO NOT hide the header anymore so the Sidebar Toggle (Hamburger/Arrow) is visible */
    /* header {visibility: hidden;} <--- REMOVED THIS */
    
    /* Card Styling */
    .metric-card {
        background-color: #1c1c1e;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 5px 0;
        color: #ffffff;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #8e8e93;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .green-text { color: #32d74b; }
    .blue-text { color: #0a84ff; }
    .red-text { color: #ff453a; }
    
    /* Button Styling - Apple Style */
    div.stButton > button {
        border-radius: 12px;
        height: 3.5em;
        font-weight: 600;
        border: none;
        background-color: #0a84ff;
        color: white;
    }
    div.stButton > button:active {
        background-color: #007aff;
    }
    
    /* Calculator Button Styling */
    div[data-testid="column"] button {
        background-color: #333333;
        color: white;
        border-radius: 50px;
        height: 70px;
        width: 70px; 
        font-size: 24px;
        margin: 0 auto;
        display: block;
    }
    div[data-testid="column"] button:hover {
        background-color: #444;
        border: 1px solid #555;
    }
    div[data-testid="column"] button:active {
        background-color: #777;
    }
    
    /* Input Fields */
    input[type="text"], input[type="number"] {
        background-color: #1c1c1e !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #1c1c1e !important;
        border-color: #333 !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1c1c1e;
    }
    section[data-testid="stSidebar"] .stRadio > label {
        font-size: 1.2rem !important;
        font-weight: bold;
        color: white;
    }
    
</style>
""", unsafe_allow_html=True)

EXPENSES_FILE = 'expenses.csv'
FUNDS_FILE = 'funds.csv'
TODO_FILE = 'todo.csv'

# --- Helper Functions ---
def get_ist_date():
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    return ist_now.date()

def load_csv(file_path, columns):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
            for col in columns:
                if col not in df.columns:
                    if col == "Done":
                        df[col] = False
                    elif col == "Mode":
                        df[col] = "Online"
                    else:
                        df[col] = ""
            if "Done" in df.columns:
                df["Done"] = df["Done"].astype(str).str.lower().isin(['true', '1', 'yes', 't'])
            return df
        except Exception as e:
            df = pd.DataFrame(columns=columns)
            if "Done" in columns:
                df["Done"] = df["Done"].astype(bool)
            return df
    else:
        df = pd.DataFrame(columns=columns)
        if "Done" in columns:
            df["Done"] = df["Done"].astype(bool)
        return df

def save_csv(df, file_path):
    df.to_csv(file_path, index=False)

# --- App Logic ---

if 'expenses' not in st.session_state:
    st.session_state.expenses = load_csv(EXPENSES_FILE, ["Date", "Item", "Category", "Amount", "Mode"])
if 'funds' not in st.session_state:
    st.session_state.funds = load_csv(FUNDS_FILE, ["Date", "Source", "Mode", "Amount"])
if 'todo' not in st.session_state:
    st.session_state.todo = load_csv(TODO_FILE, ["Item", "Notes", "Done"])

df_expenses = st.session_state.expenses
df_funds = st.session_state.funds
df_todo = st.session_state.todo

# --- Categories ---
default_categories = ["Food", "Travel", "Bills", "Shopping", "Entertainment", "Other"]
if 'Category' in df_expenses.columns:
    existing_categories = [str(x) for x in df_expenses['Category'].dropna().unique().tolist()]
else:
    existing_categories = []
combined_categories = list(set(default_categories + existing_categories))
if "Other" in combined_categories:
    combined_categories.remove("Other")
combined_categories.sort()
combined_categories.append("Other")

# --- Calculations ---
total_cash_in = df_funds[df_funds['Mode'] == 'Cash']['Amount'].sum()
total_online_in = df_funds[df_funds['Mode'] == 'Online']['Amount'].sum()

if 'Mode' in df_expenses.columns:
    total_cash_out = df_expenses[df_expenses['Mode'] == 'Cash']['Amount'].sum()
    total_online_out = df_expenses[df_expenses['Mode'] != 'Cash']['Amount'].sum()
else:
    total_cash_out = 0
    total_online_out = df_expenses['Amount'].sum()

bal_cash = total_cash_in - total_cash_out
bal_online = total_online_in - total_online_out

today_date = get_ist_date()
today_spent = df_expenses[df_expenses['Date'] == today_date]['Amount'].sum()
total_spent = df_expenses['Amount'].sum()

# --- SIDEBAR NAVIGATION ---
# Restored Sidebar Navigation
with st.sidebar:
    st.markdown("## 💰 Kharch Book")
    selected_page = st.radio(
        "Menu", 
        ["Expenses", "Wallet", "Calculator", "Analysis", "To-Buy List", "Funds History"],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("v2.4 • Mobile Sidebar Restored")

# --- PAGE ROUTING ---

# 1. EXPENSES
if selected_page == "Expenses":
    # Title (Since we don't have the top selectbox anymore)
    st.title("📝 Expenses")
    
    # Dashboard Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Cash Bal</div><div class="metric-value green-text">₹{bal_cash:,.0f}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Online Bal</div><div class="metric-value blue-text">₹{bal_online:,.0f}</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Today</div><div class="metric-value red-text">₹{today_spent:,.0f}</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total</div><div class="metric-value">₹{total_spent:,.0f}</div></div>""", unsafe_allow_html=True)

    # Add Expense Form
    with st.container(border=True):
        st.subheader("Add New Expense")
        with st.form("add_expense_form", clear_on_submit=True):
            item = st.text_input("Description", placeholder="e.g. Vegetables")
            
            c_cat, c_amt = st.columns(2)
            with c_cat:
                cat_selection = st.selectbox("Category", combined_categories)
            with c_amt:
                amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01, format="%.2f", value=None)
            
            if cat_selection == "Other":
                 custom_category = st.text_input("New Category Name")
            else:
                 custom_category = None
            
            c_mode, c_date = st.columns(2)
            with c_mode:
                mode = st.radio("Mode", ["Online", "Cash"], horizontal=True)
            with c_date:
                date = st.date_input("Date", value=get_ist_date())

            if st.form_submit_button("Add Expense", type="primary", use_container_width=True):
                final_cat = custom_category.strip() if cat_selection == "Other" and custom_category else cat_selection
                
                if item and amount is not None and amount > 0:
                    new_entry = pd.DataFrame([{
                        "Date": date, "Item": item, "Category": final_cat, "Amount": amount, "Mode": mode
                    }])
                    st.session_state.expenses = pd.concat([new_entry, st.session_state.expenses], ignore_index=True)
                    save_csv(st.session_state.expenses, EXPENSES_FILE)
                    st.toast("Saved!", icon="✅")
                    st.rerun()
                else:
                    st.error("Enter details")

    # Table
    st.write("### Transactions")
    with st.expander("🗑️ Delete Tool"):
        if not df_expenses.empty:
            del_opts = [f"{i} | {r['Date']} | {r['Item']} | ₹{r['Amount']}" for i, r in df_expenses.iterrows()]
            del_opts.reverse()
            sel_del = st.selectbox("Select item", del_opts, label_visibility="collapsed")
            if st.button("Delete Selected", type="primary"):
                idx = int(sel_del.split(" | ")[0])
                st.session_state.expenses = df_expenses.drop(idx).reset_index(drop=True)
                save_csv(st.session_state.expenses, EXPENSES_FILE)
                st.rerun()
        else:
            st.info("Empty")

    edited_expenses = st.data_editor(
        df_expenses,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount": st.column_config.NumberColumn(format="₹%.2f"),
            "Date": st.column_config.DateColumn(format="DD MMM"),
            "Category": st.column_config.SelectboxColumn(options=combined_categories, required=True),
            "Mode": st.column_config.SelectboxColumn(options=["Online", "Cash"], required=True)
        }
    )
    if not edited_expenses.equals(df_expenses):
        st.session_state.expenses = edited_expenses
        save_csv(edited_expenses, EXPENSES_FILE)
        st.rerun()

    st.divider()
    csv = df_expenses.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Backup CSV", csv, "expenses.csv", "text/csv", use_container_width=True)

# 2. WALLET
elif selected_page == "Wallet":
    st.title("💳 Wallet")
    
    # Balances
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Cash</div><div class="metric-value green-text">₹{bal_cash:,.2f}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Online</div><div class="metric-value blue-text">₹{bal_online:,.2f}</div></div>""", unsafe_allow_html=True)

    tab_add, tab_exchange = st.tabs(["➕ Add", "💱 Transfer"])
    
    with tab_add:
        with st.form("add_funds_form", clear_on_submit=True):
            f_amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01, format="%.2f", value=None)
            f_mode = st.radio("To", ["Online", "Cash"], horizontal=True)
            f_source = st.text_input("Source", placeholder="Salary, ATM")
            f_date = st.date_input("Date", value=get_ist_date())
            
            if st.form_submit_button("Add Money", type="primary", use_container_width=True):
                if f_amount is not None and f_amount > 0:
                    new_fund = pd.DataFrame([{
                        "Date": f_date,
                        "Source": f_source if f_source else "Add",
                        "Mode": "Online" if "Online" in f_mode else "Cash",
                        "Amount": f_amount
                    }])
                    df_funds = pd.concat([new_fund, df_funds], ignore_index=True)
                    st.session_state.funds = df_funds
                    save_csv(df_funds, FUNDS_FILE)
                    st.toast("Added!", icon="💰")
                    st.rerun()

    with tab_exchange:
        with st.form("transfer_form", clear_on_submit=True):
            t_amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01, format="%.2f", value=None)
            t_direction = st.radio("Type", ["Online ➔ Cash", "Cash ➔ Online"], horizontal=True)
            t_note = st.text_input("Note")
            t_date = st.date_input("Date", value=get_ist_date())
            
            if st.form_submit_button("Transfer", type="primary", use_container_width=True):
                if t_amount is not None and t_amount > 0:
                    if "Online ➔ Cash" in t_direction:
                        src, dst = "Online", "Cash"
                    else:
                        src, dst = "Cash", "Online"
                    
                    row_out = {"Date": t_date, "Source": f"Transfer to {dst}", "Mode": src, "Amount": -t_amount}
                    row_in = {"Date": t_date, "Source": f"Transfer from {src}", "Mode": dst, "Amount": t_amount}
                    
                    new_transfer = pd.DataFrame([row_out, row_in])
                    st.session_state.funds = pd.concat([new_transfer, st.session_state.funds], ignore_index=True)
                    save_csv(st.session_state.funds, FUNDS_FILE)
                    st.toast("Done!", icon="✅")
                    st.rerun()

# 3. CALCULATOR
elif selected_page == "Calculator":
    st.title("🧮 Calculator")
    
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
            st.session_state.calc_input = str(eval(st.session_state.calc_input))
        except:
            st.session_state.calc_input = "Error"

    st.markdown(f"""
    <div style="background-color: #000; padding: 20px; border-radius: 10px; text-align: right; font-family: monospace; font-size: 3rem; color: white; margin-bottom: 20px; border: 1px solid #333;">
        {st.session_state.calc_input if st.session_state.calc_input else "0"}
    </div>
    """, unsafe_allow_html=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1: st.button("C", on_click=calc_clear, use_container_width=True)
    with b2: st.button("⌫", on_click=calc_back, use_container_width=True)
    with b3: st.button("%", on_click=btn_click, args=("/100",), use_container_width=True)
    with b4: st.button("÷", on_click=btn_click, args=("/",), use_container_width=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1: st.button("7", on_click=btn_click, args=("7",), use_container_width=True)
    with b2: st.button("8", on_click=btn_click, args=("8",), use_container_width=True)
    with b3: st.button("9", on_click=btn_click, args=("9",), use_container_width=True)
    with b4: st.button("×", on_click=btn_click, args=("*",), use_container_width=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1: st.button("4", on_click=btn_click, args=("4",), use_container_width=True)
    with b2: st.button("5", on_click=btn_click, args=("5",), use_container_width=True)
    with b3: st.button("6", on_click=btn_click, args=("6",), use_container_width=True)
    with b4: st.button("–", on_click=btn_click, args=("-",), use_container_width=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1: st.button("1", on_click=btn_click, args=("1",), use_container_width=True)
    with b2: st.button("2", on_click=btn_click, args=("2",), use_container_width=True)
    with b3: st.button("3", on_click=btn_click, args=("3",), use_container_width=True)
    with b4: st.button("+", on_click=btn_click, args=("+",), use_container_width=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1: st.button("00", on_click=btn_click, args=("00",), use_container_width=True)
    with b2: st.button("0", on_click=btn_click, args=("0",), use_container_width=True)
    with b3: st.button(".", on_click=btn_click, args=(".",), use_container_width=True)
    with b4: st.button("=", on_click=calc_result, type="primary", use_container_width=True)

# 4. ANALYSIS
elif selected_page == "Analysis":
    st.title("📊 Analysis")
    if not df_expenses.empty:
        col_charts1, col_charts2 = st.columns(2)
        
        with col_charts1:
            st.markdown("##### 🍩 Expenses by Category")
            category_data = df_expenses.groupby("Category")["Amount"].sum().reset_index()
            base = alt.Chart(category_data).encode(theta=alt.Theta("Amount", stack=True))
            pie = base.mark_arc(outerRadius=120, innerRadius=80).encode(
                color=alt.Color("Category"),
                order=alt.Order("Amount", sort="descending"),
                tooltip=["Category", "Amount"]
            )
            text = base.mark_text(radius=140).encode(
                text="Amount",
                order=alt.Order("Amount", sort="descending"),
                color=alt.value("white")
            )
            st.altair_chart(pie + text, use_container_width=True)

        with col_charts2:
            st.markdown("##### 📅 Daily Spending Trend")
            daily_data = df_expenses.groupby("Date")["Amount"].sum().reset_index()
            daily_data = daily_data.sort_values("Date")
            bar_chart = alt.Chart(daily_data).mark_bar(color='#FF5252').encode(
                x=alt.X('Date', axis=alt.Axis(format='%d %b')),
                y='Amount',
                tooltip=['Date', 'Amount']
            ).interactive()
            st.altair_chart(bar_chart, use_container_width=True)
    else:
        st.info("Add some expenses to see your analytics here.")

# 5. FUNDS HISTORY
elif selected_page == "Funds History":
    st.title("💰 Funds History")
    
    edited_funds = st.data_editor(
        df_funds,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount": st.column_config.NumberColumn(format="₹%.2f"),
            "Date": st.column_config.DateColumn(format="DD MMM YYYY")
        }
    )
    if not edited_funds.equals(df_funds):
        st.session_state.funds = edited_funds
        save_csv(edited_funds, FUNDS_FILE)
        st.rerun()

# 6. TO-BUY LIST
elif selected_page == "To-Buy List":
    if "todo_title" not in st.session_state:
        st.session_state.todo_title = "🛍️ Shopping List"
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        new_title = st.text_input("List Name", value=st.session_state.todo_title, label_visibility="collapsed")
        if new_title != st.session_state.todo_title:
            st.session_state.todo_title = new_title
    
    st.title(st.session_state.todo_title)
    st.caption("Tick items when bought, then click 'Clean Up' to remove them.")

    if not df_todo.empty:
        df_todo["Done"] = df_todo["Done"].fillna(False).astype(bool)
        if "Item" in df_todo.columns:
            df_todo["Item"] = df_todo["Item"].fillna("").astype(str)
        if "Notes" in df_todo.columns:
            df_todo["Notes"] = df_todo["Notes"].fillna("").astype(str)
    else:
        df_todo = pd.DataFrame(columns=["Done", "Item", "Notes"])
        df_todo["Done"] = df_todo["Done"].astype(bool)
        df_todo["Item"] = df_todo["Item"].astype(str)
        df_todo["Notes"] = df_todo["Notes"].astype(str)
        st.session_state.todo = df_todo

    edited_todo = st.data_editor(
        df_todo,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Done": st.column_config.CheckboxColumn("Bought?", default=False, width="small"),
            "Item": st.column_config.TextColumn("Item Name", width="medium", required=True),
            "Notes": st.column_config.TextColumn("Notes", width="large")
        }
    )

    if not edited_todo.equals(df_todo):
        st.session_state.todo = edited_todo
        save_csv(edited_todo, TODO_FILE)
        st.rerun()

    if not edited_todo.empty and edited_todo['Done'].any():
        st.write("")
        col_clean1, col_clean2 = st.columns([1, 4])
        with col_clean1:
            if st.button("🗑️ Clean Up", type="primary", help="Remove all checked items"):
                df_remaining = edited_todo[edited_todo['Done'] == False]
                st.session_state.todo = df_remaining.reset_index(drop=True)
                save_csv(st.session_state.todo, TODO_FILE)
                st.toast("Cleaned!", icon="🧹")
                st.rerun()
