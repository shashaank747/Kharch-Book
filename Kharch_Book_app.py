import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import os

# --- Configuration ---
st.set_page_config(page_title="Kharch Book", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for UI Polish ---
st.markdown("""
<style>
    /* Main Background adjustments */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Card Styling */
    .metric-card {
        background-color: #262730;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.4);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 5px 0;
        color: #ffffff;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #a0a0a0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .green-text { color: #4CAF50; }
    .blue-text { color: #2196F3; }
    .red-text { color: #FF5252; }
    
    /* Button Styling Override */
    div.stButton > button {
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    
    /* Calculator Button specific styling */
    div[data-testid="column"] button {
        background-color: #2b2d3e;
        color: white;
        border: none;
    }
    div[data-testid="column"] button:hover {
        background-color: #3b3d54;
        border-color: #555;
    }
    /* Make equal button blue */
    div[data-testid="column"] button[kind="primary"] {
        background-color: #2196F3 !important;
        color: white !important;
    }
    
    /* Hide default header */
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

EXPENSES_FILE = 'expenses.csv'
FUNDS_FILE = 'funds.csv'

# --- Helper Functions ---
def load_csv(file_path, columns):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
            for col in columns:
                if col not in df.columns:
                    df[col] = "Online" if col == "Mode" else ""
            return df
        except Exception as e:
            return pd.DataFrame(columns=columns)
    else:
        return pd.DataFrame(columns=columns)

def save_csv(df, file_path):
    df.to_csv(file_path, index=False)

# --- App Logic ---

# 1. Load Data
if 'expenses' not in st.session_state:
    st.session_state.expenses = load_csv(EXPENSES_FILE, ["Date", "Item", "Category", "Amount", "Mode"])
if 'funds' not in st.session_state:
    st.session_state.funds = load_csv(FUNDS_FILE, ["Date", "Source", "Mode", "Amount"])

df_expenses = st.session_state.expenses
df_funds = st.session_state.funds

# --- Calculations for Dashboard ---
# Total Funds In
total_cash_in = df_funds[df_funds['Mode'] == 'Cash']['Amount'].sum()
total_online_in = df_funds[df_funds['Mode'] == 'Online']['Amount'].sum()

# Total Spent
if 'Mode' in df_expenses.columns:
    total_cash_out = df_expenses[df_expenses['Mode'] == 'Cash']['Amount'].sum()
    total_online_out = df_expenses[df_expenses['Mode'] != 'Cash']['Amount'].sum()
else:
    total_cash_out = 0
    total_online_out = df_expenses['Amount'].sum()

bal_cash = total_cash_in - total_cash_out
bal_online = total_online_in - total_online_out

# Daily Spend
today_date = datetime.now().date()
today_spent = df_expenses[df_expenses['Date'] == today_date]['Amount'].sum()
total_spent = df_expenses['Amount'].sum()

# --- SIDEBAR: Wallet ---
with st.sidebar:
    st.markdown("## 💳 **Wallet Manager**")
    st.info("Add your salary or cash withdrawals here to track balances.")
    
    with st.form("add_funds_form", clear_on_submit=True):
        f_amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
        f_mode = st.radio("Destination", ["Online (Bank/UPI)", "Cash"], horizontal=True)
        f_source = st.text_input("Source", placeholder="e.g. Salary, ATM")
        
        if st.form_submit_button("💰 Add Funds", type="primary", use_container_width=True):
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
                st.success("Added!")
                st.rerun()
    
    st.divider()
    st.caption(f"v1.3 • Data saved to CSV")

# --- MAIN PAGE ---
st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>💰 Kharch Book</h1>", unsafe_allow_html=True)

# 1. Dashboard Cards (HTML/CSS)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Cash Balance</div>
        <div class="metric-value green-text">₹{bal_cash:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Online Balance</div>
        <div class="metric-value blue-text">₹{bal_online:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Spent Today</div>
        <div class="metric-value red-text">₹{today_spent:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Spent</div>
        <div class="metric-value">₹{total_spent:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# 2. Add Expense Form
with st.container():
    st.markdown("### 📝 **New Entry**")
    with st.form("add_expense_form", clear_on_submit=True, border=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            item = st.text_input("Description", placeholder="What did you buy?")
            category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Entertainment", "Other"])
        
        with col2:
            # Smart Layout for Amount and Mode
            c_a, c_b = st.columns([2, 1])
            with c_a:
                amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
            with c_b:
                st.write("") # Spacer to align
                st.write("") 
                mode = st.radio("Pay Mode", ["Online", "Cash"], horizontal=False, label_visibility="collapsed")
            
            date = st.date_input("Date", datetime.now())

        # Full width button
        if st.form_submit_button("Add Expense", type="primary", use_container_width=True):
            if item and amount > 0:
                new_entry = pd.DataFrame([{
                    "Date": date,
                    "Item": item,
                    "Category": category,
                    "Amount": amount,
                    "Mode": mode
                }])
                st.session_state.expenses = pd.concat([new_entry, st.session_state.expenses], ignore_index=True)
                save_csv(st.session_state.expenses, EXPENSES_FILE)
                st.toast("Saved!", icon="✅")
                st.rerun()
            else:
                st.error("Please enter description and amount")

# 3. Data & Tools Tabs
st.write("")
tab1, tab2, tab3, tab4 = st.tabs(["📜 Expense Log", "📊 Analysis", "💳 Funds History", "📥 Export"])

with tab1:
    # Delete Tool
    with st.expander("🗑️ Delete Tool"):
        if not df_expenses.empty:
            del_opts = [f"{i} | {r['Date']} | {r['Item']} | ₹{r['Amount']}" for i, r in df_expenses.iterrows()]
            del_opts.reverse()
            sel_del = st.selectbox("Select item to delete", del_opts, label_visibility="collapsed")
            if st.button("Delete Selected Expense", type="primary"):
                idx = int(sel_del.split(" | ")[0])
                st.session_state.expenses = df_expenses.drop(idx).reset_index(drop=True)
                save_csv(st.session_state.expenses, EXPENSES_FILE)
                st.rerun()
        else:
            st.info("No expenses to delete.")

    # Main Table
    edited_expenses = st.data_editor(
        df_expenses,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Amount": st.column_config.NumberColumn(format="₹%.2f"),
            "Date": st.column_config.DateColumn(format="DD MMM YYYY"),
            "Mode": st.column_config.SelectboxColumn(options=["Online", "Cash"], required=True)
        }
    )
    if not edited_expenses.equals(df_expenses):
        st.session_state.expenses = edited_expenses
        save_csv(edited_expenses, EXPENSES_FILE)
        st.rerun()

with tab2:
    if not df_expenses.empty:
        col_charts1, col_charts2 = st.columns(2)
        
        # 1. Category Breakdown (Donut Chart)
        with col_charts1:
            st.markdown("##### 🍩 Expenses by Category")
            category_data = df_expenses.groupby("Category")["Amount"].sum().reset_index()
            
            base = alt.Chart(category_data).encode(
                theta=alt.Theta("Amount", stack=True)
            )
            
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

        # 2. Daily Trend (Bar Chart)
        with col_charts2:
            st.markdown("##### 📅 Daily Spending Trend")
            daily_data = df_expenses.groupby("Date")["Amount"].sum().reset_index()
            # Ensure proper sorting by date
            daily_data = daily_data.sort_values("Date")
            
            bar_chart = alt.Chart(daily_data).mark_bar(color='#FF5252').encode(
                x=alt.X('Date', axis=alt.Axis(format='%d %b')),
                y='Amount',
                tooltip=['Date', 'Amount']
            ).interactive()
            
            st.altair_chart(bar_chart, use_container_width=True)
    else:
        st.info("Add some expenses to see your analytics here.")

with tab3:
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

with tab4:
    st.warning("Ensure you download this backup periodically.")
    csv = df_expenses.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Expenses (CSV)", csv, "expenses.csv", "text/csv", use_container_width=True)

# --- Calculator Section (Bottom) ---
st.divider()
with st.expander("🧮 **Calculator**", expanded=True):
    # Calculator Logic
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

    # Display
    st.markdown(f"""
    <div style="background-color: #000; padding: 10px; border-radius: 5px; text-align: right; font-family: monospace; font-size: 24px; color: white; margin-bottom: 10px; border: 1px solid #333;">
        {st.session_state.calc_input if st.session_state.calc_input else "0"}
    </div>
    """, unsafe_allow_html=True)

    # Grid
    # We use columns to create the grid layout
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
