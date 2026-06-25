import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="2026 World Cup Analyzer", page_icon="🏆", layout="centered")
st.title("🏆 2026 World Cup Group Stage Simulator")
st.markdown("Welcome to your interactive World Cup standings dashboard! This app processes live match data and calculates group rankings automatically.")

# --- CONNECT TO YOUR LIVE RENDER API ---
# Replace this string with your exact live Render URL
API_URL = "https://worldcup-2026-api-zmw8.onrender.com/matches"

@st.cache_data(ttl=300)  # Caches the data for 5 minutes to keep the app fast
def load_live_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json().get("data", [])
        return []
    except Exception:
        return []

live_matches = load_live_data()

if not live_matches:
    st.error("Could not fetch live data from the API. Please ensure your Render backend is running.")
    st.stop()

# --- CONNECT TO YOUR LIVE RENDER API ---

@st.cache_data(ttl=60)  
def load_live_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json().get("data", [])
        return []
    except Exception:
        return []

live_matches = load_live_data()

# --- PROCESS LIVE DATA INTO STANDINGS ---

all_known_teams = [
    "Mexico", "South Africa", "Korea Republic", "Czechia",
    "Canada", "Bosnia-Herzegovina", "Qatar", "Switzerland",
    "Haiti", "Scotland", "Brazil", "Morocco",
    "United States", "Paraguay", "Australia", "Türkiye",
    "Germany", "Curaçao", "Côte d'Ivoire", "Ecuador",
    "Netherlands", "Japan", "Sweden", "Tunisia",
    "Belgium", "Egypt", "IR Iran", "New Zealand",
    "Spain", "Cape Verde", "Saudi Arabia", "Uruguay",
    "France", "Senegal", "Iraq", "Norway",
    "Argentina", "Algeria", "Austria", "Jordan",
    "Portugal", "Congo DR", "Uzbekistan", "Colombia",
    "England", "Croatia", "Ghana", "Panama"
]

teams = {t: {"PTS": 0, "GF": 0, "GA": 0} for t in all_known_teams}

for match in live_matches:
    home = match.get("home_team", "").strip()
    away = match.get("away_team", "").strip()
    score_str = match.get("score", "").strip()
    
    if not home or not away or not score_str:
        continue
        

    if home not in teams or away not in teams:
        continue
        
    if "v" in score_str.lower():
        continue
        
    
    score_str = score_str.replace("–", "-").replace("—", "-") 
    
    if "-" in score_str:
        try:
            
            parts = score_str.split("-")
            gh = int(parts[0].strip())
            ga = int(parts[1].strip())
            
            teams[home]["GF"] += gh
            teams[home]["GA"] += ga
            teams[away]["GF"] += ga
            teams[away]["GA"] += gh
            
            
            if gh > ga:
                teams[home]["PTS"] += 3
            elif gh < ga:
                teams[away]["PTS"] += 3
            else:
                teams[home]["PTS"] += 1
                teams[away]["PTS"] += 1
        except Exception:

            continue
# If no matches have been played yet, generate empty structure using groups
if not teams:
    all_known_teams = ["Mexico", "South Africa", "Korea Republic", "Czechia", "Canada", "Bosnia-Herzegovina", "Qatar", "Switzerland", "Haiti", "Scotland", "Brazil", "Morocco", "United States", "Paraguay", "Australia", "Türkiye", "Germany", "Curaçao", "Côte d'Ivoire", "Ecuador", "Netherlands", "Japan", "Sweden", "Tunisia", "Belgium", "Egypt", "IR Iran", "New Zealand", "Spain", "Cape Verde", "Saudi Arabia", "Uruguay", "France", "Senegal", "Iraq", "Norway", "Argentina", "Algeria", "Austria", "Jordan", "Portugal", "Congo DR", "Uzbekistan", "Colombia", "England", "Croatia", "Ghana", "Panama"]
    for t in all_known_teams:
        teams[t] = {"PTS": 0, "GF": 0, "GA": 0}

standings = pd.DataFrame.from_dict(teams, orient="index").reset_index()
standings.rename(columns={"index": "Team"}, inplace=True)
standings["GD"] = standings["GF"] - standings["GA"]

# --- GROUPS DICTIONARY ---
groups = {
    "Group A": ["Mexico", "South Africa", "Korea Republic", "Czechia"],
    "Group B": ["Canada", "Bosnia-Herzegovina", "Qatar" ,  "Switzerland" ],
    "Group C": ["Haiti", "Scotland", "Brazil", "Morocco"],
    "Group D": ["United States" , "Paraguay", "Australia", "Türkiye"],
    "Group E": ["Germany", "Curaçao","Côte d'Ivoire", "Ecuador" ],
    "Group F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "Group G": ["Belgium", "Egypt","IR Iran", "New Zealand" ],
    "Group H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "Group I": ["France", "Senegal", "Iraq", "Norway"],
    "Group J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "Group K": ["Portugal", "Congo DR", "Uzbekistan", "Colombia"],
    "Group L": ["England", "Croatia","Ghana", "Panama"],
}

# --- EXPLORE GROUP STANDINGS ---
st.header("🔍 Explore Group Standings")
selected_group = st.selectbox("Choose a Group to display:", list(groups.keys()))

if selected_group:
    team_list = groups[selected_group]
    group_df = standings[standings["Team"].isin(team_list)].copy()
    group_df = group_df.sort_values(
        by=["PTS", "GD", "GF", "GA"], ascending=[False, False, False, False]
    ).reset_index(drop=True)
    
    st.subheader(f"📊 Live Standings: {selected_group}")
    st.dataframe(group_df[["Team", "PTS", "GD", "GF", "GA"]], use_container_width=True)

st.divider()

# --- TEAM STATISTICS LOOKUP ---
st.header("⚽ Team Statistics Lookup")
all_teams_list = sorted(standings["Team"].unique())
selected_team = st.selectbox("Select a Team to view its tournament summary:", all_teams_list)

if selected_team:
    team_stats = standings[standings["Team"] == selected_team].iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Points (PTS)", value=int(team_stats["PTS"]))
    col2.metric(label="Goal Difference (GD)", value=int(team_stats["GD"]))
    col3.metric(label="Goals For (GF)", value=int(team_stats["GF"]))
    col4.metric(label="Goals Against (GA)", value=int(team_stats["GA"]))

st.divider()

# --- ADVANCED TOURNAMENT LEADERBOARDS ---
st.header("📋 Advanced Tournament Leaderboards")
st.markdown("Use the selector below to filter and analyze unified standings across different categories.")

view_option = st.selectbox(
    "Select a view:",
    [
        "📊 Overall Standings (All 48 Teams)",
        "⭐ Arab Nations Standings",
        "🕒 3rd-Place Teams Tracker (Top 8 Qualify)"
    ]
)

if view_option == "📊 Overall Standings (All 48 Teams)":
    st.subheader("🌍 Universal Leaderboard")
    overall_df = standings.sort_values(by=['PTS', 'GD', 'GF'], ascending=[False, False, False]).reset_index(drop=True)
    overall_df.index = overall_df.index + 1
    overall_df.index.name = "Rank"
    st.dataframe(overall_df[['Team', 'PTS', 'GD', 'GF', 'GA']], use_container_width=True)

elif view_option == "⭐ Arab Nations Standings":
    st.subheader("Regional Leaderboard: Arab Nations")
    arab_teams_list = ['Algeria', 'Morocco', 'Saudi Arabia', 'Egypt', 'Tunisia', 'Qatar', 'Jordan', 'Iraq']
    arab_df = standings[standings['Team'].isin(arab_teams_list)].copy()
    
    if not arab_df.empty:
        arab_df = arab_df.sort_values(by=['PTS', 'GD', 'GF'], ascending=[False, False, False]).reset_index(drop=True)
        arab_df.index = arab_df.index + 1
        arab_df.index.name = "Rank"
        st.dataframe(arab_df[['Team', 'PTS', 'GD', 'GF', 'GA']], use_container_width=True)
    else:
        st.info("No stats available for Arab nations yet.")

elif view_option == "🕒 3rd-Place Teams Tracker (Top 8 Qualify)":
    st.subheader("🎟️ Best 3rd-Placed Teams Leaderboard")
    st.markdown("In the 48-team format, the **top 8 best third-placed teams** advance to the Round of 32.")
    
    third_placed_teams = []
    for g_name, g_teams in groups.items():
        g_df = standings[standings['Team'].isin(g_teams)].copy()
        g_df = g_df.sort_values(by=['PTS', 'GD', 'GF', 'GA'], ascending=[False, False, False, False]).reset_index(drop=True)
        if len(g_df) >= 3:
            third_placed_teams.append(g_df.iloc[2])
            
    if third_placed_teams:
        third_df = pd.DataFrame(third_placed_teams).sort_values(by=['PTS', 'GD', 'GF'], ascending=[False, False, False]).reset_index(drop=True)
        third_df.index = third_df.index + 1
        third_df.index.name = "Rank"
        
        third_df['Status'] = ['✅ Qualified (Top 8)' if i <= 8 else '❌ Eliminated' for i in third_df.index]
        
        def highlight_qualified(row):
            return ['background-color: #d4edda; color: #155724;' if row['Status'] == '✅ Qualified (Top 8)' else '' for _ in row]
            
        styled_third_df = third_df[['Team', 'PTS', 'GD', 'GF', 'GA', 'Status']].style.apply(highlight_qualified, axis=1)
        st.dataframe(styled_third_df, use_container_width=True)
    else:
        st.info("Group stage data is updating.")

st.divider()
st.header("📊 Tournament Leaderboards")
col_attack, col_defense = st.columns(2)

with col_attack:
    st.subheader("🔥 Top 5 Attacks")
    top_attacks = standings.nlargest(5, 'GF')[['Team', 'GF', 'PTS']]
    top_attacks.index = range(1, 6)
    st.dataframe(top_attacks, use_container_width=True)

with col_defense:
    st.subheader("🛡️ Top 5 Defenses")
    top_defenses = standings.nsmallest(5, 'GA')[['Team', 'GA', 'PTS']]
    top_defenses.index = range(1, 6)
    st.dataframe(top_defenses, use_container_width=True)
