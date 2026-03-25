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
    
    sports_emojis = {
        'AFL': '🏉',
        'NBA': '🏀',
        'NFL': '🏈',
        'MLB': '⚾',
        'WORLD CUP': '⚽'
    }
    
    sports_columns = list(sports_emojis.keys())
    df[sports_columns] = df[sports_columns].fillna(0)
    
    # 2. Logic for Top Scorer Badges & The Milk of Shame
    team_badges = {team: "" for team in df['Team']}
    
    # Find the top scorers
    for sport, emoji in sports_emojis.items():
        max_score = df[sport].max()
        if max_score > 0:
            top_teams = df[df[sport] == max_score]['Team'].tolist()
            for team in top_teams:
                team_badges[team] += f"{emoji}"
                
    # Find the lowest NBA scorer (The Milk)
    min_nba = df['NBA'].min()
    lowest_nba_teams = df[df['NBA'] == min_nba]['Team'].tolist()
    for team in lowest_nba_teams:
        team_badges[team] += "🥛"
                
    # Apply badges
    df['Team_Display'] = df['Team'].apply(lambda x: f"{x} {team_badges.get(x, '')}")
    
    # 3. Overall Standings Ladder
    st.header("Overall Standings")
    
    # Sort by total points
    overall_cols = ['Team_Display', 'Points', 'AFL', 'NBA', 'NFL', 'MLB', 'WORLD CUP']
    overall_df = df[overall_cols].sort_values(by='Points', ascending=False).reset_index(drop=True)
    
    # Add podium medals to the top 3
    medals = ['🥇', '🥈', '🥉']
    for i in range(min(3, len(overall_df))):
        # Insert the medal at the front of the name
        overall_df.at[i, 'Team_Display'] = f"{medals[i]} {overall_df.at[i, 'Team_Display']}"
    
    overall_df.index = overall_df.index + 1 # Start rank at 1
    overall_df = overall_df.rename(columns={'Team_Display': 'Team'})
    
    # Spotlight the current leader
    if not overall_df.empty:
        leader_name = overall_df.iloc[0]['Team']
        leader_points = overall_df.iloc[0]['Points']
        st.success(f"**Current Leader:** {leader_name} with {leader_points} points! 👑")

    # Display the dataframe with a visual Progress Bar for the Points
    max_total_points = float(overall_df['Points'].max())
    st.dataframe(
        overall_df, 
        use_container_width=True,
        column_config={
            "Points": st.column_config.ProgressColumn(
                "Total Points",
                help="Visual gap to first place",
                format="%d",
                min_value=0,
                max_value=max_total_points,
            ),
        }
    )
    
    st.divider()
    
    # 4. Individual Sport Ladders
    st.header("Individual Sport Ladders")
    cols = st.columns(3)
    
    for i, (sport, emoji) in enumerate(sports_emojis.items()):
        col = cols[i % 3]
        with col:
            st.subheader(f"{emoji} {sport}")
            sport_df = df[['Team_Display', sport]].sort_values(by=sport, ascending=False).reset_index(drop=True)
            sport_df.index = sport_df.index + 1
            sport_df = sport_df.rename(columns={'Team_Display': 'Team'})
            st.dataframe(sport_df, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data. Please check your Google Sheet format. Error: {e}")
