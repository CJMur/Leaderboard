import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cumulative Fantasy Leaderboard", layout="wide")
st.title("🏆 Fantasy Sports Cumulative Leaderboard")

# 1. Fetching the data
SHEET_ID = "1RxniymerCt2S9-Y8VzVgL0J21hABiV0kpqSP_hc5L_8"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=600)
def load_data():
    return pd.read_csv(CSV_URL)

try:
    df = load_data()
    
    # Define the sports and their corresponding emojis for the badges
    sports_emojis = {
        'AFL': '🏉',
        'NBA': '🏀',
        'NFL': '🏈',
        'MLB': '⚾',
        'WORLD CUP': '⚽'
    }
    
    sports_columns = list(sports_emojis.keys())
    df[sports_columns] = df[sports_columns].fillna(0)
    
    # 2. Logic for Top Scorer Badges
    # Create a dictionary to hold the badges for each team
    team_badges = {team: "" for team in df['Team']}
    
    # Loop through each sport, find the max score, and award the badge
    for sport, emoji in sports_emojis.items():
        max_score = df[sport].max()
        if max_score > 0:  # Only award if someone has actually scored points
            top_teams = df[df[sport] == max_score]['Team'].tolist()
            for team in top_teams:
                team_badges[team] += f" {emoji}"
                
    # Create a new display name that includes the badges
    df['Team_Display'] = df['Team'].apply(lambda x: f"{x}{team_badges.get(x, '')}")
    
    # 3. Overall Standings Ladder
    st.header("Overall Standings")
    st.write("The current masters of the multi-sport universe. Badges indicate the top scorer in a specific sport!")
    
    # Pull the relevant columns, sort by the 'Points' column from your sheet, and rename the display column
    overall_cols = ['Team_Display', 'Points', 'AFL', 'NBA', 'NFL', 'MLB', 'WORLD CUP']
    overall_df = df[overall_cols].sort_values(by='Points', ascending=False).reset_index(drop=True)
    overall_df.index = overall_df.index + 1 # Start rank at 1
    overall_df = overall_df.rename(columns={'Team_Display': 'Team'})
    
    st.dataframe(overall_df, use_container_width=True)
    
    st.divider()
    
    # 4. Individual Sport Ladders
    st.header("Individual Sport Ladders")
    
    # Create three columns to display the ladders side-by-side nicely
    cols = st.columns(3)
    
    for i, (sport, emoji) in enumerate(sports_emojis.items()):
        # Cycle through the 3 columns so they wrap nicely
        col = cols[i % 3]
        with col:
            st.subheader(f"{emoji} {sport}")
            
            # Filter, sort, and display just that sport
            sport_df = df[['Team_Display', sport]].sort_values(by=sport, ascending=False).reset_index(drop=True)
            sport_df.index = sport_df.index + 1
            sport_df = sport_df.rename(columns={'Team_Display': 'Team'})
            
            st.dataframe(sport_df, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data. Please check your Google Sheet format. Error: {e}")
