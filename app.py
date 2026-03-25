import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cumulative Fantasy Leaderboard", layout="wide")
st.title("🏆 Fantasy Sports Cumulative Leaderboard")
st.write("*Note: NBA points are worth double!*")

# 1. Fetching the data
SHEET_ID = "1RxniymerCt2S9-Y8VzVgL0J21hABiV0kpqSP_hc5L_8"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=600)
def load_data():
    return pd.read_csv(CSV_URL)

try:
    df = load_data()
    
    # 2. Clean and Calculate Data
    # Fill any empty cells with 0 just in case someone forgets to type it
    sports_columns = ['AFL', 'NBA', 'NFL', 'MLB', 'WORLD CUP']
    df[sports_columns] = df[sports_columns].fillna(0)
    
    # Apply the 2x multiplier to NBA points
    df['NBA (Doubled)'] = df['NBA'] * 2
    
    # Calculate the true total points
    df['Total Points'] = df['AFL'] + df['NBA (Doubled)'] + df['NFL'] + df['MLB'] + df['WORLD CUP']
    
    # 3. Build the Leaderboard
    # Select the columns we want to show and sort them by the new Total Points
    display_cols = ['Team', 'AFL', 'NBA', 'NBA (Doubled)', 'NFL', 'MLB', 'WORLD CUP', 'Total Points']
    leaderboard = df[display_cols].sort_values(by='Total Points', ascending=False).reset_index(drop=True)
    
    # Start the index at 1 for ranking purposes
    leaderboard.index = leaderboard.index + 1 
    
    # Display the table
    st.dataframe(leaderboard, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data. Please check your Google Sheet format. Error: {e}")
