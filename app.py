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
    
    # Strip any hidden whitespace from team names
    df['Team'] = df['Team'].astype(str).str.strip()
    
    sports_emojis = {
        'AFL': '🏉',
        'NBA': '🏀',
        'NFL': '🏈',
        'MLB': '⚾',
        'WORLD CUP': '⚽'
    }
    
    sports_columns = list(sports_emojis.keys())
    
    # Ensure current year sports columns have 0s instead of NaNs
    for col in sports_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # 2. Logic for Top Scorer Badges & The Milk of Shame
    team_badges = {team: "" for team in df['Team']}
    
    # Find current top scorers
    for sport, emoji in sports_emojis.items():
        if sport in df.columns:
            max_score = df[sport].max()
            if max_score > 0:
                top_teams = df[df[sport] == max_score]['Team'].tolist()
                for team in top_teams:
                    team_badges[team] += f"{emoji}"
                
    # Find lowest NBA scorer (strictly excluding Alf and Jack)
    if 'NBA' in df.columns:
        eligible_for_milk = df[~df['Team'].isin(['Alf', 'Jack'])]
        if not eligible_for_milk.empty:
            min_nba = eligible_for_milk['NBA'].min()
            lowest_nba_teams = eligible_for_milk[eligible_for_milk['NBA'] == min_nba]['Team'].tolist()
            for team in lowest_nba_teams:
                team_badges[team] += "🥛"
                
    # Apply current year badges
    df['Team_Display'] = df['Team'].apply(lambda x: f"{x} {team_badges.get(x, '')}")
    
    # 3. Build the Historical Trophy Cabinet
    def build_trophy_cabinet(row):
        cabinet = ""
        total_titles = 0
        for sport, emoji in sports_emojis.items():
            title_col = f"{sport} Titles" # Make sure this matches your Google Sheet column headers!
            if title_col in df.columns:
                # Fill any empty title cells with 0 and count them
                count = int(pd.to_numeric(row.get(title_col), errors='coerce') or 0)
                cabinet += emoji * count
                total_titles += count
        return cabinet, total_titles

    # Apply the trophy logic to create two new columns
    df[['Trophy Cabinet', 'Total Titles']] = df.apply(
        lambda row: pd.Series(build_trophy_cabinet(row)), axis=1
    )

    # 4. Layout: Split the top section
    top_left_col, top_right_col = st.columns([2.5, 1]) # 2.5 ratio for standings, 1 ratio for titles
    
    with top_left_col:
        st.header("Overall Standings")
        
        # Sort by total points FIRST, then NBA score SECOND
        overall_cols = ['Team', 'Team_Display', 'Points', 'AFL', 'NBA', 'NFL', 'MLB', 'WORLD CUP']
        overall_df = df[overall_cols].sort_values(by=['Points', 'NBA'], ascending=[False, False]).reset_index(drop=True)
        
        # Add podium medals to the top 3
        medals = ['🥇', '🥈', '🥉']
        for i in range(min(3, len(overall_df))):
            overall_df.at[i, 'Team_Display'] = f"{medals[i]} {overall_df.at[i, 'Team_Display']}"
        
        overall_df.index = overall_df.index + 1 # Start rank at 1
        
        # Clean up dataframe for display
        display_df = overall_df[['Team_Display', 'Points', 'AFL', 'NBA', 'NFL', 'MLB', 'WORLD CUP']].copy()
        display_df = display_df.rename(columns={'Team_Display': 'Team'})
        
        # Logic to bold the leader's row using Pandas Styling
        def bold_leader_row(row):
            # If it's the first row (index 1), make the font bold
            if row.name == display_df.index[0]:
                return ['font-weight: bold'] * len(row)
            return [''] * len(row)

        styled_display_df = display_df.style.apply(bold_leader_row, axis=1)
        
        # Spotlight the current leader
        if not overall_df.empty:
            leader_name = overall_df.iloc[0]['Team']
            leader_points = overall_df.iloc[0]['Points']
            st.success(f"**Current Leader:** {leader_name} with {leader_points} points! 👑")

        # Display the dataframe
        max_total_points = float(display_df['Points'].max())
        st.dataframe(
            styled_display_df, 
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

    with top_right_col:
        st.header("Hall of Fame 🏆")
        st.write("Historical titles won.")
        
        # Filter down to just Team and their Trophies, sort by who has the most titles
        hof_df = df[['Team', 'Trophy Cabinet', 'Total Titles']].copy()
        hof_df = hof_df[hof_df['Total Titles'] > 0] # Only show people who actually have a title
        hof_df = hof_df.sort_values(by='Total Titles', ascending=False).reset_index(drop=True)
        hof_df.index = hof_df.index + 1
        
        # Drop the helper count column so only the emojis show
        st.dataframe(hof_df[['Team', 'Trophy Cabinet']], use_container_width=True)

    st.divider()
    
    # 5. Individual Sport Ladders
    st.header("Individual Sport Ladders")
    cols = st.columns(3)
    
    for i, (sport, emoji) in enumerate(sports_emojis.items()):
        if sport in df.columns:
            col = cols[i % 3]
            with col:
                st.subheader(f"{emoji} {sport}")
                sport_df = df[['Team_Display', sport]].sort_values(by=sport, ascending=False).reset_index(drop=True)
                sport_df.index = sport_df.index + 1
                sport_df = sport_df.rename(columns={'Team_Display': 'Team'})
                st.dataframe(sport_df, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data. Please check your Google Sheet format. Error: {e}")
