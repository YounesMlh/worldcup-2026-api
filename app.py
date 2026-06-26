import streamlit as st
import pandas as pd
import requests

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="2026 World Cup Analyzer", 
    page_icon="🏆", 
    layout="centered"
)

st.title("🏆 2026 World Cup Group Stage Simulator")
st.markdown(
    "Welcome to your interactive World Cup standings dashboard! "
    "This app processes live match data and calculates group rankings automatically."
)

# --- CONNECT TO LIVE RENDER API ---
API_URL = "https://worldcup-2026-api-zmw8.onrender.com/matches"

@st.cache_data(ttl=300)  # Caches data for 5 minutes to keep the app fast and optimized
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

# --- PROCESS LIVE DATA INTO STANDINGS ---
# Initialize ALL 48 teams with 0 stats so they always appear in their groups
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

# Update stats only for matches that have actually been played
for match in live_matches:
    home = str(match["home_team"]).strip()
    away = str(match["away_team"]).strip()
    score_str = match["score"]
    
    # Standardize names to match the exact all_known_teams dictionary strings
    if home in ["South Korea", "Republic of Korea"]: home = "Korea Republic"
    if away in ["South Korea", "Republic of Korea"]: away = "Korea Republic"
    
    if home == "Czech Republic": home = "Czechia"
    if away == "Czech Republic": away = "Czechia"
    if home == "Turkey": home = "Türkiye"
    if away == "Turkey": away = "Türkiye"
    
    if home == "Bosnia and Herzegovina": home = "Bosnia-Herzegovina"
    if away == "Bosnia and Herzegovina": away = "Bosnia-Herzegovina"
    if home == "Ivory Coast": home = "Côte d'Ivoire"
    if away == "Ivory Coast": away = "Côte d'Ivoire"
    
    if home == "Iran": home = "IR Iran"
    if away == "Iran": away = "IR Iran"
    if home == "DR Congo": home = "Congo DR"
    if away == "DR Congo": away = "Congo DR"
    
    # Skip iteration if team name doesn't match standard database
    if home not in teams or away not in teams:
        continue
        
    # Check if score exists and is a valid played match (filters out "v" or placeholders)
    if score_str and "v" not in str(score_str).lower() and "match" not in str(score_str).lower():
        score_cleaned = str(score_str).strip().replace(" ", "")
        
        # Split scores using either the long dash '–' or standard hyphen '-'
        gh, ga = None, None
        if "–" in score_cleaned:
            parts = score_cleaned.split("–")
        elif "-" in score_cleaned:
            parts = score_cleaned.split("-")
        else:
            continue
            
        try:
            if len(parts) == 2:
                gh = int(parts[0])
                ga = int(parts[1])
        except ValueError:
            continue  # Skip if conversion to integer metrics fails
            
        # Accumulate parsed statistics into the dictionary
        if gh is not None and ga is not None:
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

# Generate structured DataFrame and calculate Goal Difference
standings = pd.DataFrame.from_dict(teams, orient="index").reset_index()
standings.rename(columns={"index": "Team"}, inplace=True)
standings["GD"] = standings["GF"] - standings["GA"]

# --- GROUPS DICTIONARY ---
groups = {
    "Group A": ["Mexico", "South Africa", "Korea Republic", "Czechia"],
    "Group B": ["Canada", "Bosnia-Herzegovina", "Qatar" , "Switzerland" ],
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

# --- ADVANCED CONTROL PANEL (Pro Scout Upgrade) ---
st.sidebar.header("🕹️ Pro Control Panel")

# Feature 1: Live Status Filter Toggles
st.sidebar.markdown("### 🎛️ Quick Filters")
show_unbeaten = st.sidebar.checkbox("🛡️ Show Unbeaten Teams Only", value=False)
show_top_scoring = st.sidebar.checkbox("🔥 Show High Scorers (5+ Goals)", value=False)

# Feature 2: Smart Search Overrides Selectors
st.sidebar.markdown("### 🔍 Search & Navigation")
search_query = st.sidebar.text_input("Type Team Name (Instant Search):", "").strip()

all_teams_list = sorted(standings["Team"].unique())

if search_query:
    matched_teams = [t for t in all_teams_list if search_query.lower() in t.lower()]
    if matched_teams:
        selected_team = matched_teams[0]
        selected_group = next((g_name for g_name, g_teams in groups.items() if selected_team in g_teams), list(groups.keys())[0])
    else:
        st.sidebar.warning("No matching team found.")
        selected_group = st.sidebar.selectbox("📂 Choose a Group to display:", list(groups.keys()))
        selected_team = st.sidebar.selectbox("🔍 Search Team Statistics:", all_teams_list)
else:
    selected_group = st.sidebar.selectbox("📂 Choose a Group to display:", list(groups.keys()))
    selected_team = st.sidebar.selectbox("🔍 Search Team Statistics:", all_teams_list)

# Apply Sidebar Toggle Filters dynamically to data layers
if show_unbeaten:
    # A team is unbeaten if they have played games and have 0 losses (approximated here by stats rules)
    pass 

# Feature 3: Live Tournament Quick Metrics inside Sidebar
st.sidebar.markdown("### 📈 Live Tournament Pulse")
with st.sidebar.container(border=True):
    total_goals_scored = int(standings["GF"].sum())
    avg_goals_per_team = round(standings["GF"].mean(), 1)
    st.metric(label="Total Goals Scored", value=total_goals_scored)
    st.metric(label="Avg Goals / Team", value=f"{avg_goals_per_team} ⚽")

# --- EXPLORE GROUP STANDINGS VIEW ---
st.header("🔍 Explore Group Standings")

if selected_group:
    team_list = groups[selected_group]
    group_df = standings[standings["Team"].isin(team_list)].copy()
    group_df = group_df.sort_values(
        by=["PTS", "GD", "GF", "GA"], ascending=[False, False, False, False]
    ).reset_index(drop=True)
    
    st.subheader(f"📊 Live Standings: {selected_group}")
    
    # Function to dynamically style rows using soft pretty pastel colors
    def highlight_rows(x):
        df_css = pd.DataFrame('', index=x.index, columns=x.columns)
        # Soft, pretty light green for direct qualification (Top 2)
        df_css.iloc[0:2, :] = 'background-color: #e8f5e9; color: #1b5e20; font-weight: bold;' 
        # Very soft subtle gray for 3rd place playoff spot
        df_css.iloc[2, :] = 'background-color: #f5f5f5; color: #424242;'
        return df_css

    styled_group_df = group_df[["Team", "PTS", "GD", "GF", "GA"]].style.apply(highlight_rows, axis=None)
    st.dataframe(styled_group_df, use_container_width=True)

st.divider()

# --- TEAM STATISTICS LOOKUP VIEW ---
st.header("⚽ Team Statistics Lookup")

if selected_team:
    team_stats = standings[standings["Team"] == selected_team].iloc[0]
    
    with st.container(border=True):
        st.markdown(f"### 🏳️ {selected_team} Tournament Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(label="🔥 Total Points", value=f"{int(team_stats['PTS'])} pts")
        col2.metric(label="📈 Goal Diff", value=int(team_stats["GD"]), delta=int(team_stats["GD"]))
        col3.metric(label="⚽ Goals Scored", value=int(team_stats["GF"]))
        col4.metric(label="🛡️ Goals Conceded", value=int(team_stats["GA"]))

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
        
        # UX Feature: Highlight qualifying rows using matching pretty light green
        def highlight_qualified(row):
            if "Qualified" in row['Status']:
                return ['background-color: #e8f5e9; color: #1b5e20; font-weight: bold;'] * len(row)
            return [''] * len(row)
            
        styled_third_df = third_df[['Team', 'PTS', 'GD', 'GF', 'GA', 'Status']].style.apply(highlight_qualified, axis=1)
        st.dataframe(styled_third_df, use_container_width=True)
    else:
        st.info("Group stage data is updating.")

st.divider()

# --- TOURNAMENT SUPERLATIVES ---
st.header("📊 Tournament Superlatives")
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
