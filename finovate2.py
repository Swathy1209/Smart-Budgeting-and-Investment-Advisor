import streamlit as st
import pandas as pd
import sqlite3
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import zipfile

# Set page configuration (MUST be the first Streamlit command)
st.set_page_config(
    page_title="Smart Budgeting and Investment Advisor",
    page_icon="💰",
    layout="wide"
)


# Database setup
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    category TEXT,
    amount REAL,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT
)
""")

conn.commit()

# Sidebar navigation with icons
menu_options = {
    "Home": "🏠",
    "Expense Tracker": "💵",
    "Budget Planner": "📊",
    "Investment Advisor": "💎",
    "Stock Analysis": "📈",
    "Login/Signup": "🔐"
}
menu = st.sidebar.radio("Navigation", list(menu_options.keys()), format_func=lambda x: f"{menu_options[x]} {x}")

# Home Page
if menu == "Home":
    st.title("Smart Budgeting and Investment Advisor")
    st.markdown("""
    Welcome to your personal finance hub! Here's what you can do:
    - Track and analyze your expenses.
    - Plan your budget and achieve your savings goals.
    - Get personalized investment advice.
    - Analyze stock market trends.
    """)
    st.image("https://via.placeholder.com/800x400.png?text=Financial+Freedom+Awaits", use_column_width=True)

# Login/Signup
elif menu == "Login/Signup":
    st.header("Login or Signup")
    choice = st.radio("Select", ["Login", "Signup"], horizontal=True)

    if choice == "Signup":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Signup"):
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            st.success("Signup successful! Please login.")

    elif choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
            if user:
                st.success("Login successful!")
            else:
                st.error("Invalid credentials.")

# Expense Tracker
elif menu == "Expense Tracker":
    st.header(" Expense Tracker")
    category = st.selectbox("Category", ["Food", "Rent", "Transportation", "Healthcare", "Education", "Insurance", "Debt Payments", "Savings", "Miscellaneous"])
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    date = st.date_input("Date")

    if st.button("Add Expense"):
        cursor.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)", (category, amount, str(date)))
        conn.commit()
        st.success("Expense added successfully!")

    st.subheader("Expense Summary")
    data = pd.read_sql_query("SELECT * FROM expenses", conn)
    if not data.empty:
        st.dataframe(data)
        fig = px.pie(data, names="category", values="amount", title="Expense Distribution")
        st.plotly_chart(fig, use_container_width=True)

# Budget Planner
elif menu == "Budget Planner":
    st.header(" Budget Planner")
    income = st.number_input("Monthly Income", min_value=0.0, step=0.01)
    savings_goal = st.number_input("Savings Goal", min_value=0.0, step=0.01)

    if income > 0:
        recommended_budget = income - savings_goal
        st.write(f"Your recommended budget for expenses: ₹{recommended_budget:.2f}")

# Investment Advisor
elif menu == "Investment Advisor":
    st.header("Investment Advisor")

    # User Inputs for Investment Preferences
    age = st.number_input("Enter your age", min_value=18, max_value=100, step=1)
    risk_appetite = st.selectbox("Select your risk appetite", ["Low", "Medium", "High"])
    investment_goal = st.selectbox("What is your investment goal?", ["Short-term", "Medium-term", "Long-term"])
    amount_to_invest = st.number_input("Amount you want to invest (in ₹)", min_value=1000, step=100)

    # Logic for Recommendation
    if st.button("Get Recommendations"):
        try:
            # Example Recommendation Logic
            if risk_appetite == "Low":
                st.write("Recommended Investments:")
                st.markdown("""
                - *Fixed Deposits (FDs)*: Secure and stable returns.  
                - *Government Bonds*: Low risk, decent returns.  
                - *Index Funds*: Low-cost passive investments.
                """)
            elif risk_appetite == "Medium":
                st.write("Recommended Investments:")
                st.markdown("""
                - *Mutual Funds*: Balanced funds for medium risk and returns.  
                - *Blue-Chip Stocks*: Reliable large-cap companies.  
                - *Exchange-Traded Funds (ETFs)*: Diversified and cost-effective.
                """)
            elif risk_appetite == "High":
                st.write("Recommended Investments:")
                st.markdown("""
                - *Stocks*: Small-cap and mid-cap for high growth.  
                - *Cryptocurrency*: High-risk, high-reward potential.  
                - *Real Estate*: High upfront cost but potential long-term rewards.
                """)

            # Display Investment Goal Summary
            st.info(f"Based on your goal of {investment_goal} investment, consider diversifying your portfolio.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
# Stock Analysis
elif menu == "Stock Analysis":
    st.header("Stock Analysis")

    # Path to the ZIP file
    zip_file_path = "c:/Users/swathiga/Downloads/stocks.zip"

    try:
        # Extract and load the CSV file
        with zipfile.ZipFile(zip_file_path, 'r') as z:
            csv_files = [f for f in z.namelist() if f.endswith('.csv') and not f.startswith('__MACOSX/')]
            if len(csv_files) != 1:
                st.error(f"Expected one CSV file, but found {len(csv_files)}: {csv_files}")
            else:
                csv_file = csv_files[0]
                with z.open(csv_file) as f:
                    stocks_data = pd.read_csv(f)

                # Display data
                st.subheader("Stock Data Overview")
                st.dataframe(stocks_data.head())

                # Descriptive Statistics
                st.subheader("Descriptive Statistics")
                descriptive_stats = stocks_data.groupby('Ticker')['Close'].describe()
                st.write(descriptive_stats)

                # Time Series Analysis
                stocks_data['Date'] = pd.to_datetime(stocks_data['Date'])
                pivot_data = stocks_data.pivot(index='Date', columns='Ticker', values='Close')

                st.subheader("Time Series Analysis")
                fig = make_subplots(rows=1, cols=1)
                for column in pivot_data.columns:
                    fig.add_trace(
                        go.Scatter(x=pivot_data.index, y=pivot_data[column], name=column),
                        row=1, col=1
                    )
                fig.update_layout(title_text='Time Series of Closing Prices', xaxis_title='Date', yaxis_title='Closing Price')
                st.plotly_chart(fig)

                # Volatility Analysis
                st.subheader("Volatility Analysis")
                volatility = pivot_data.std().sort_values(ascending=False)
                fig = px.bar(volatility, x=volatility.index, y=volatility.values, labels={'y': 'Standard Deviation', 'x': 'Ticker'}, title='Volatility of Closing Prices')
                st.plotly_chart(fig)

                # Correlation Analysis
                st.subheader("Correlation Analysis")
                correlation_matrix = pivot_data.corr()
                fig = go.Figure(data=go.Heatmap(
                    z=correlation_matrix,
                    x=correlation_matrix.columns,
                    y=correlation_matrix.columns,
                    colorscale='blues',
                    colorbar=dict(title='Correlation')
                ))
                fig.update_layout(title='Correlation Matrix of Closing Prices')
                st.plotly_chart(fig)

                # Risk vs. Return Analysis
                st.subheader("Risk vs. Return Analysis")
                daily_returns = pivot_data.pct_change().dropna()
                avg_daily_return = daily_returns.mean()
                risk = daily_returns.std()
                risk_return_df = pd.DataFrame({'Risk': risk, 'Average Daily Return': avg_daily_return})
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=risk_return_df['Risk'],
                    y=risk_return_df['Average Daily Return'],
                    mode='markers+text',
                    text=risk_return_df.index,
                    textposition="top center",
                    marker=dict(size=10)
                ))
                fig.update_layout(title='Risk vs. Return Analysis', xaxis_title='Risk (Standard Deviation)', yaxis_title='Average Daily Return')
                st.plotly_chart(fig)
    except FileNotFoundError:
        st.error("Stock data file not found.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
# Footer
st.sidebar.markdown("""
---
Developed by *Your Name*  
🌐 [Visit my portfolio](#)
""")
