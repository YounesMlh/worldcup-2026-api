import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import random

# --- ADVANCED PLATFORM CONFIGURATION ---
st.set_page_config(
    page_title="2026 FIFA World Cup Analytics Center", 
    page_icon="🏆", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise Styling Injection
st.markdown("""
    <style>
    .metric-card { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; font-size: 14px; }
    
    /* Big Full-Width Start Button custom styling override */
    div.stButton > button.element-container-compiled-start {
        background-color: #2563eb;
        color: white;
        font-size: 26px !important;
        font-weight: bold;
        padding: 25px 0px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button.element-container-compiled-start:hover {
        background-color: #1d4ed8;
        transform: scale(1.01);
    }
    </style>
""", unsafe_allow_html=True)


# --- GLOBAL CROSS-USER LEADERBOARD CACHE ---
@st.cache_resource
def get_global_scoreboard():
    return {
        "Names": ["Zidane", "Pelé", "Maradona"],
        "Scores": [14, 12, 11]
    }

global_data = get_global_scoreboard()


# --- DEEP 50 HISTORIC WORLD CUP QUESTIONS DATABASE ---
QUIZ_POOL = [
    {"q": "Which country won the first ever World Cup in 1930?", "o": ["Argentina", "Uruguay", "Brazil", "Italy"], "a": "Uruguay"},
    {"q": "Who is the all-time top goalscorer in World Cup history?", "o": ["Miroslav Klose", "Ronaldo", "Pelé", "Messi"], "a": "Miroslav Klose"},
    {"q": "Which nation has won the most World Cup titles?", "o": ["Germany", "Italy", "Argentina", "Brazil"], "a": "Brazil"},
    {"q": "Which player holds the record for most World Cup match appearances?", "o": ["Lothar Matthäus", "Lionel Messi", "Cristiano Ronaldo", "Diego Maradona"], "a": "Lionel Messi"},
    {"q": "Who scored the famous 'Hand of God' goal in 1986?", "o": ["Pelé", "Diego Maradona", "Zinedine Zidane", "Romário"], "a": "Diego Maradona"},
    {"q": "Which country hosted the 2010 FIFA World Cup?", "o": ["Brazil", "South Africa", "Germany", "Japan"], "a": "South Africa"},
    {"q": "Who won the Best Young Player award at the 2018 World Cup?", "o": ["Kylian Mbappé", "Luka Modrić", "Neymar", "Paul Pogba"], "a": "Kylian Mbappé"},
    {"q": "Which country is the reigning World Cup Champion from 2022?", "o": ["France", "Croatia", "Argentina", "Morocco"], "a": "Argentina"},
    {"q": "What unique feat did Zinedine Zidane achieve in the 2006 Final?", "o": ["Scored a hat-trick", "Got a red card", "Saved a penalty", "Scored an own goal"], "a": "Got a red card"},
    {"q": "How many teams will compete in the expanded 2026 World Cup?", "o": ["32", "40", "48", "64"], "a": "48"},
    {"q": "Which country won its first World Cup title in 2010?", "o": ["Netherlands", "Spain", "Portugal", "England"], "a": "Spain"},
    {"q": "Who was the captain of the 1970 World Cup-winning Brazil team?", "o": ["Carlos Alberto", "Pelé", "Garrincha", "Jairzinho"], "a": "Carlos Alberto"},
    {"q": "Which team was infamously defeated 7-1 by Germany in 2014?", "o": ["Argentina", "Brazil", "France", "Portugal"], "a": "Brazil"},
    {"q": "Who scored the winning goal for Germany in the 2014 Final?", "o": ["Thomas Müller", "Miroslav Klose", "Mario Götze", "Toni Kroos"], "a": "Mario Götze"},
    {"q": "Which animal was the official mascot for the 2010 World Cup?", "o": ["Leopard (Zakumi)", "Armadillo (Fuleco)", "Lion (Goleo)", "Wolf (Zabivaka)"], "a": "Leopard (Zakumi)"},
    {"q": "Which goalkeeper made the iconic triple save against Italy in 1970?", "o": ["Gordon Banks", "Lev Yashin", "Sepp Maier", "Dino Zoff"], "a": "Gordon Banks"},
    {"q": "In which World Cup did Morocco become the first African nation to reach the semifinals?", "o": ["2010", "2014", "2018", "2022"], "a": "2022"},
    {"q": "Who won the Golden Ball award at the 2014 World Cup despite losing the final?", "o": ["Thomas Müller", "Lionel Messi", "Arjen Robben", "James Rodríguez"], "a": "Lionel Messi"},
    {"q": "Which nation played in three World Cup finals (1974, 1978, 2010) but never won?", "o": ["Sweden", "Hungary", "Netherlands", "Croatia"], "a": "Netherlands"},
    {"q": "Who is the oldest goalscorer in FIFA World Cup history?", "o": ["Roger Milla", "Pelé", "Cristiano Ronaldo", "Zlatan Ibrahimović"], "a": "Roger Milla"},
    {"q": "Which country won back-to-back World Cups in 1958 and 1962?", "o": ["Italy", "Germany", "Brazil", "Uruguay"], "a": "Brazil"},
    {"q": "Which country hosted the World Cup in 1994?", "o": ["Italy", "United States", "France", "Japan"], "a": "United States"},
    {"q": "Who scored the fastest goal in World Cup history (11 seconds)?", "o": ["Hakan Şükür", "Bryan Robson", "Clint Dempsey", "Ronaldo"], "a": "Hakan Şükür"},
    {"q": "Which country was banned from the 1950 World Cup because of WWII?", "o": ["Germany", "Italy", "Argentina", "Uruguay"], "a": "Germany"},
    {"q": "Who scored a hat-trick in the 1966 World Cup Final for England?", "o": ["Geoff Hurst", "Bobby Charlton", "Bobby Moore", "Gary Lineker"], "a": "Geoff Hurst"},
    {"q": "Which country made its tournament debut at the 2018 World Cup?", "o": ["Iceland", "Togo", "Angola", "Slovakia"], "a": "Iceland"},
    {"q": "Who is the only manager to win two consecutive World Cups?", "o": ["Vittorio Pozzo", "Mário Zagallo", "Franz Beckenbauer", "Didier Deschamps"], "a": "Vittorio Pozzo"},
    {"q": "Which company has made every official World Cup match ball since 1970?", "o": ["Nike", "Adidas", "Puma", "Umbro"], "a": "Adidas"},
    {"q": "What was the scoreline of the 2018 World Cup Final between France and Croatia?", "o": ["1-0", "2-1", "3-2", "4-2"], "a": "4-2"},
    {"q": "Who was the breakout Colombian top scorer at the 2014 World Cup?", "o": ["Radamel Falcao", "James Rodríguez", "Juan Cuadrado", "Jackson Martínez"], "a": "James Rodríguez"},
    {"q": "Which country lost the 1990 final to West Germany on a late penalty?", "o": ["Argentina", "Italy", "England", "Brazil"], "a": "Argentina"},
    {"q": "Which host country failed to advance past the group stage first time in history?", "o": ["South Africa", "Qatar", "Japan", "USA"], "a": "South Africa"},
    {"q": "Which goalkeeper won the Golden Glove at the 2022 World Cup?", "o": ["Hugo Lloris", "Emiliano Martínez", "Yassine Bounou", "Dominik Livaković"], "a": "Emiliano Martínez"},
    {"q": "Who holds the record for most World Cup titles as a player?", "o": ["Pelé", "Maradona", "Ronaldo Nazário", "Cafu"], "a": "Pelé"},
    {"q": "Which African nation did England narrowly defeat 3-2 in a 1990 thriller?", "o": ["Cameroon", "Nigeria", "Egypt", "Morocco"], "a": "Cameroon"},
    {"q": "Which country won the World Cup hosted on home soil in 1998?", "o": ["Italy", "Germany", "France", "Brazil"], "a": "France"},
    {"q": "Who was sent off for biting Giorgio Chiellini in 2014?", "o": ["Luis Suárez", "Neymar", "Zlatan Ibrahimović", "Diego Costa"], "a": "Luis Suárez"},
    {"q": "Which European nation hosted the tournament in 2006?", "o": ["France", "Germany", "Italy", "Austria"], "a": "Germany"},
    {"q": "Who did Zinedine Zidane headbutt during the 2006 World Cup Final?", "o": ["Marco Materazzi", "Fabio Cannavaro", "Gennaro Gattuso", "Gianluigi Buffon"], "a": "Marco Materazzi"},
    {"q": "Which nation won the tournament in 1954 in a match known as the Miracle of Bern?", "o": ["West Germany", "Hungary", "Austria", "Uruguay"], "a": "West Germany"},
    {"q": "What color card was introduced to the World Cup for the first time in 1970?", "o": ["Yellow & Red Cards", "Blue Cards", "Green Cards", "White Cards"], "a": "Yellow & Red Cards"},
    {"q": "Who won the Golden Boot at the 2002 World Cup with 8 goals?", "o": ["Ronaldo Nazário", "Rivaldo", "Miroslav Klose", "Thierry Henry"], "a": "Ronaldo Nazário"},
    {"q": "Which country qualified for its first ever World Cup in 2006?", "o": ["Angola", "Senegal", "Nigeria", "South Africa"], "a": "Angola"},
    {"q": "Who missed the decisive penalty for Italy in the 1994 Final shootout?", "o": ["Roberto Baggio", "Franco Baresi", "Paolo Maldini", "Gianfranco Zola"], "a": "Roberto Baggio"},
    {"q": "Which city hosted the final match of the 2022 World Cup in Qatar?", "o": ["Doha", "Lusail", "Al Rayyan", "Al Wakrah"], "a": "Lusail"},
    {"q": "Which team was knocked out without conceding a single goal in 2006?", "o": ["Switzerland", "Italy", "France", "England"], "a": "Switzerland"},
    {"q": "Who scored four goals in a single match during the 2018 World Cup?", "o": ["No one did", "Harry Kane", "Cristiano Ronaldo", "Kylian Mbappé"], "a": "No one did"},
    {"q": "Which Asian country surprised the world by reaching the 2002 Semifinals?", "o": ["Japan", "South Korea", "Saudi Arabia", "China"], "a": "South Korea"},
    {"q": "Who is the only player to score in two different World Cup finals for different countries?", "o": ["Robert Prosinečki", "Dejan Stanković", "Luis Monti", "Michel Platini"], "a": "Luis Monti"},
    {"q": "Which nation will play host to the grand final match of the 2026 World Cup?", "o": ["United States", "Mexico", "Canada", "Morocco"], "a": "United States"}
]


# --- ENGINE FLAGS & SESSION STATE ARCHITECTURE ---
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = random.sample(QUIZ_POOL, 15)
    st.session_state.quiz_user_answers = {}
    st.session_state.quiz_active = False
    st.session_state.quiz_submitted = False
    st.session_state.last_score_announcement = ""


# --- COMPACT RENDERING LOGIC HUB ---
st.markdown("### 🏆 Arena Trivia Challenge Matrix")

# --- VIEW 1: COLLAPSED BIG BUTTON VIEW ---
if not st.session_state.quiz_active:
    if st.session_state.last_score_announcement:
        st.success(st.session_state.last_score_announcement)

    # Big full-width button to initialize the quiz frame
    if st.button("🚀 START 15-QUESTION TRIVIA ARENA", use_container_width=True, key="start_btn_compiled"):
        st.session_state.quiz_questions = random.sample(QUIZ_POOL, 15)
        st.session_state.quiz_user_answers = {}
        st.session_state.quiz_active = True
        st.session_state.quiz_submitted = False
        st.rerun()

# --- VIEW 2: EXPANDED ACTIVE QUESTION VIEW ---
else:
    with st.form("quiz_form"):
        st.info("⏱️ Complete all 15 inputs to register your nickname ranking below!")
        
        for i, item in enumerate(st.session_state.quiz_questions):
            st.markdown(f"**Q{i+1}: {item['q']}**")
            st.session_state.quiz_user_answers[i] = st.radio(
                f"Selection Options Matrix Q{i+1}", 
                options=item['o'], 
                key=f"q_radio_{i}",
                label_visibility="collapsed"
            )
            st.write("---")
            
        username = st.text_input("👤 Leaderboard Nickname Key:", max_chars=20)
        submit_quiz = st.form_submit_button("Submit & Lock Analytics Classification", use_container_width=True)

    if submit_quiz:
        if not username.strip():
            st.error("Invalid entry string! A valid profile nickname is required to file performance tracking records.")
        else:
            final_score = 0
            for i, item in enumerate(st.session_state.quiz_questions):
                if st.session_state.quiz_user_answers[i] == item['a']:
                    final_score += 1
                    
            # Update shared resource cache matrix dictionary
            global_data["Names"].append(username.strip())
            global_data["Scores"].append(final_score)
            
            # Record current status performance string before closing form view context
            st.session_state.last_score_announcement = f"🎉 Sequence Evaluation Complete! {username} earned score entry: **{final_score}/15**."
            
            # Collapse app states directly back down onto the initial state logic view tree
            st.session_state.quiz_submitted = True
            st.session_state.quiz_active = False
            st.rerun()


# --- ALWAYS ACCESSIBLE DYNAMIC SCOREBOARD BLOCK ---
if st.session_state.quiz_submitted or not st.session_state.quiz_active:
    st.subheader("📊 Global Trivia Classification Leaderboard")
    st.markdown("_Live global cache updating simultaneously on connection streams across Render cluster endpoints._")

    leaderboard_df = pd.DataFrame(global_data).sort_values(by="Scores", ascending=False).reset_index(drop=True)
    leaderboard_df.index += 1

    st.dataframe(
        leaderboard_df.rename(columns={"Names": "COMPETITOR", "Scores": "CORRECT ANSWERS (OUT OF 15)"}),
        use_container_width=True
    )

st.write("---")
st.markdown("## ⚽ Proceed to 2026 Tournament Operations Matrix")


# --- CORE DASHBOARD SYSTEM CONTROLLER ---
st.title("🏆 2026 FIFA World Cup Live Analytics Center")
st.markdown("---")


# --- 1. ROBUST CORE SCRAPER ENGINE ---
WIKI_URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup"

@st.cache_data(ttl=300)
def fetch_live_group_stage_payload():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(WIKI_URL, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        match_payload = []
        match_containers = soup.find_all("div", class_="footballbox")
        
        for box in match_containers:
            try:
                home = box.find("th", class_="fhome").text.strip()
                away = box.find("th", class_="faway").text.strip()
                score = box.find("th", class_="fscore").text.strip()
                match_payload.append({"home_team": home, "away_team": away, "score": score})
            except AttributeError:
                continue
        return match_payload
    except Exception:
        return []

live_matches = fetch_live_group_stage_payload()


# --- 2. STANDARDIZED DATA PROCESSING PIPELINE ---
all_known_teams = [
    "Mexico", "South Africa", "Korea Republic", "Czechia", "Canada", "Bosnia-Herzegovina", "Qatar", "Switzerland",
    "Haiti", "Scotland", "Brazil", "Morocco", "United States", "Paraguay", "Australia", "Türkiye",
    "Germany", "Curaçao", "Côte d'Ivoire", "Ecuador", "Netherlands", "Japan", "Sweden", "Tunisia",
    "Belgium", "Egypt", "IR Iran", "New Zealand", "Spain", "Cape Verde", "Saudi Arabia", "Uruguay",
    "France", "Senegal", "Iraq", "Norway", "Argentina", "Algeria", "Austria", "Jordan",
    "Portugal", "Congo DR", "Uzbekistan", "Colombia", "England", "Croatia", "Ghana", "Panama"
]

team_matrix = {t: {"W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "PTS": 0} for t in all_known_teams}

def normalize_string(team_name):
    aliases = {
        "South Korea": "Korea Republic", "Republic of Korea": "Korea Republic",
        "Czech Republic": "Czechia", "Turkey": "Türkiye",
        "Bosnia and Herzegovina": "Bosnia-Herzegovina", "Ivory Coast": "Côte d'Ivoire",
        "Iran": "IR Iran", "DR Congo": "Congo DR", "Cabo Verde": "Cape Verde"
    }
    return aliases.get(team_name, team_name)

for match in live_matches:
    home = normalize_string(str(match["home_team"]).strip())
    away = normalize_string(str(match["away_team"]).strip())
    score_str = match["score"]
    
    if home not in team_matrix or away not in team_matrix:
        continue
        
    if score_str and "v" not in str(score_str).lower() and "match" not in str(score_str).lower():
        score_cleaned = str(score_str).strip().replace(" ", "")
        parts = score_cleaned.split("–") if "–" in score_cleaned else score_cleaned.split("-")
        try:
            if len(parts) == 2:
                gh, ga = int(parts[0]), int(parts[1])
                team_matrix[home]["GF"] += gh; team_matrix[home]["GA"] += ga
                team_matrix[away]["GF"] += ga; team_matrix[away]["GA"] += gh
                
                if gh > ga:
                    team_matrix[home]["PTS"] += 3; team_matrix[home]["W"] += 1; team_matrix[away]["L"] += 1
                elif gh < ga:
                    team_matrix[away]["PTS"] += 3; team_matrix[away]["W"] += 1; team_matrix[home]["L"] += 1
                else:
                    team_matrix[home]["PTS"] += 1; team_matrix[away]["PTS"] += 1
                    team_matrix[home]["D"] += 1; team_matrix[away]["D"] += 1
        except ValueError:
            continue

standings_df = pd.DataFrame.from_dict(team_matrix, orient="index").reset_index().rename(columns={"index": "Team"})
standings_df["GD"] = standings_df["GF"] - standings_df["GA"]

groups_registry = {
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


# --- 3. CONTROLS & SIDEBAR PANEL ---
st.sidebar.header("🕹️ Enterprise Filter Hub")
selected_group = st.sidebar.selectbox("📂 Select Structural Group:", list(groups_registry.keys()))
selected_team = st.sidebar.selectbox("🔍 Isolate Team Profile:", sorted(standings_df["Team"].unique()))


# --- 4. DATA PRESENTATION LAYER (GRID ARCHITECTURE) ---
col_left_panel, col_right_panel = st.columns([1, 1], gap="large")

with col_left_panel:
    st.header("📊 Group Stage Standings Matrix")
    
    group_teams = groups_registry[selected_group]
    filtered_group_df = standings_df[standings_df["Team"].isin(group_teams)].sort_values(
        by=["PTS", "GD", "GF", "GA"], ascending=[False, False, False, False]
    ).reset_index(drop=True)
    
    def inject_table_styles(val):
        styles_df = pd.DataFrame('', index=val.index, columns=val.columns)
        styles_df.iloc[0:2, :] = 'background-color: rgba(61, 141, 122, 0.6); color: #000000; font-weight: bold;'
        return styles_df

    styled_view = filtered_group_df[["Team", "W", "D", "L", "PTS", "GD", "GF"]].style.apply(inject_table_styles, axis=None)
    st.dataframe(styled_view, use_container_width=True, hide_index=True)

    st.subheader("📋 Advanced Global Analytics Leaders")
    view_tier = st.selectbox("Switch Scope View:", ["Universal Performance Sheet (48 Teams)", "Arab Nations Cohort", "Third-Place Wildcard Playoff Grid"])
    
    if view_tier == "Universal Performance Sheet (48 Teams)":
        ov_df = standings_df.sort_values(by=['PTS', 'GD', 'GF'], ascending=[False, False, False]).reset_index(drop=True)
        ov_df.index += 1
        st.dataframe(ov_df[['Team', 'W', 'D', 'L', 'PTS', 'GD']], use_container_width=True)
    elif view_tier == "Arab Nations Cohort":
        arab_tags = ['Algeria', 'Morocco', 'Saudi Arabia', 'Egypt', 'Tunisia', 'Qatar', 'Jordan', 'Iraq']
        ar_df = standings_df[standings_df['Team'].isin(arab_tags)].sort_values(by=['PTS', 'GD'], ascending=[False, False]).reset_index(drop=True)
        st.dataframe(ar_df[['Team', 'W', 'D', 'PTS', 'GD']], use_container_width=True, hide_index=True)
    elif view_tier == "Third-Place Wildcard Playoff Grid":
        third_place_pool = []
        for g_lbl, g_list in groups_registry.items():
            sorted_g = standings_df[standings_df['Team'].isin(g_list)].sort_values(by=['PTS', 'GD'], ascending=[False, False]).reset_index(drop=True)
            if len(sorted_g) >= 3: third_place_pool.append(sorted_g.iloc[2])
        if third_place_pool:
            w_df = pd.DataFrame(third_place_pool).sort_values(by=['PTS', 'GD'], ascending=[False, False]).reset_index(drop=True)
            w_df.index += 1
            w_df['Cutoff Status'] = ['✅ Qualified Phase 2' if i <= 8 else '❌ Elimination Boundary' for i in w_df.index]
            st.dataframe(w_df[['Team', 'PTS', 'GD', 'Cutoff Status']], use_container_width=True)

with col_right_panel:
    st.header("🎯 Isolated Performance Metrics")
    profile = standings_df[standings_df["Team"] == selected_team].iloc[0]
    
    st.markdown(f"#### 🏳️ {selected_team} Statistical Overview")
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Tournament Points", f"{int(profile['PTS'])} PTS")
    m_col2.metric("Goal Differential", f"{int(profile['GD'])}")
    m_col3.metric("Record Profile", f"{profile['W']}W - {profile['D']}D - {profile['L']}L")

    # --- 5. ENTERPRISE GOLDEN BOOT SYSTEM ---
    st.markdown("---")
    st.header("🥾 Golden Boot Standings")
    
    scorers_payload = {
        "Player Asset": ["Lionel Messi", "Kylian Mbappé", "Ousmane Dembélé", "Vinícius Júnior", "Erling Haaland", "Deniz Undav"],
        "Association": ["Argentina", "France", "France", "Brazil", "Norway", "Germany"],
        "Goals (G)": [6, 4, 4, 4, 4, 3],
        "Assists (A)": [0, 2, 1, 1, 0, 2]
    }
    boot_df = pd.DataFrame(scorers_payload).sort_values(by=["Goals (G)", "Assists (A)"], ascending=[False, False]).reset_index(drop=True)
    boot_df.index += 1
    boot_df.index.name = "Rank Position"
    st.dataframe(boot_df, use_container_width=True)

st.markdown("---")


# --- PRODUCTION-GRADE READ-ONLY TOURNAMENT TREE SYSTEM ---
st.header("🏁 Knockout Phase Structural Tree")
st.markdown("Official tournament bracket mapping. Future stages initialize automatically as real matches conclude.")

immutable_knockout_tree = {
    "M73": {"t1": "Germany", "t2": "Paraguay", "s1": 1, "s2": 1, "status": "FT (3-4 pen)", "date": "June 29", "winner": "Paraguay"},
    "M74": {"t1": "South Africa", "t2": "Canada", "s1": 0, "s2": 1, "status": "FT", "date": "June 28", "winner": "Canada"},
    "M75": {"t1": "Brazil", "t2": "Japan", "s1": 2, "s2": 1, "status": "FT", "date": "June 29", "winner": "Brazil"},
    "M78": {"t1": "Morocco", "t2": "Netherlands", "s1": 1, "s2": 1, "status": "FT (3-2 pen)", "date": "June 29", "winner": "Morocco"},
    
    "M76": {"t1": "Ivory Coast", "t2": "Norway", "s1": 0, "s2": 0, "status": "Scheduled", "date": "June 30", "winner": None},
    "M77": {"t1": "France", "t2": "Sweden", "s1": 0, "s2": 0, "status": "Scheduled", "date": "June 30", "winner": None},
    "M79": {"t1": "Mexico", "t2": "Ecuador", "s1": 0, "s2": 0, "status": "Scheduled", "date": "June 30", "winner": None},
    "M80": {"t1": "England", "t2": "DR Congo", "s1": 0, "s2": 0, "status": "Scheduled", "date": "July 1", "winner": None},
    "M81": {"t1": "United States", "t2": "Bosnia and Herzegovina", "s1": 0, "s2": 0, "status": "Scheduled", "date": "July 1", "winner": None},
    "M82": {"t1": "Belgium", "t2": "Senegal", "s1": 0, "s2": 0, "status": "Scheduled", "date": "July 1", "winner": None},
    "M83": {"t1": "Portugal", "t2": "Croatia", "s1": 0, "s2": 0, "status": "Scheduled", "date": "July 2", "winner": None},
    "M84": {"t1": "Spain", "t2": "Austria", "s1": 0, "s2": 0, "status": "Scheduled", "date": "July 2", "winner": None},
    "M87": {"t1": "Switzerland", "t2": "Algeria", "s1": 0, "s2": 0, "status": "Scheduled", "date": "July 2", "winner": None},
    "M85": {"t1": "Argentina", "t2": "Cape Verde", "s1": 0, "s2": 0, "status": "Scheduled", "date": "July 3", "winner": None},
    "M86": {"t1": "Australia", "t2": "Egypt", "s1": 0, "s2": 0, "status": "Scheduled", "date": "July 3", "winner": None},
    "M88": {"t1": "Colombia", "t2": "Ghana", "s1": 0, "s2": 0, "status": "Scheduled", "date": "July 3", "winner": None}
}

structural_bracket_flow = ["M73", "M77", "M74", "M78", "M83", "M84", "M81", "M82", "M75", "M76", "M79", "M80", "M85", "M86", "M87", "M88"]

tree_tabs = st.tabs(["Round of 32", "Round of 16", "Quarter-Finals", "Semi-Finals & Final"])


# --- PROFESSIONAL CARD RENDERER COMPONENT ---
def render_professional_card(match_id, data):
    is_scheduled = data["status"] == "Scheduled"
    badge_color = "#6c757d" if is_scheduled else "#0d6efd"
    
    st.markdown(f"""
    <div style="background-color: #ffffff; padding: 16px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;">
            <span style="font-size: 12px; font-weight: 700; color: #475569;">📊 MATCH {match_id}</span>
            <span style="font-size: 11px; background-color: {badge_color}; color: white; padding: 2px 8px; border-radius: 20px; font-weight: 600;">{data['status']}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; min-height: 28px;">
            <span style="font-size: 14px; font-weight: { '700; color: #1e293b;' if data['winner'] == data['t1'] else '500; color: #64748b;' }">
                🥇 {normalize_string(data['t1'])}
            </span>
            <span style="font-size: 16px; font-family: monospace; font-weight: 700; background-color: #f8fafc; padding: 2px 8px; border-radius: 4px;">
                { '-' if is_scheduled else data['s1'] }
            </span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; min-height: 28px; margin-top: 4px;">
            <span style="font-size: 14px; font-weight: { '700; color: #1e293b;' if data['winner'] == data['t2'] else '500; color: #64748b;' }">
                🥇 {normalize_string(data['t2'])}
            </span>
            <span style="font-size: 16px; font-family: monospace; font-weight: 700; background-color: #f8fafc; padding: 2px 8px; border-radius: 4px;">
                { '-' if is_scheduled else data['s2'] }
            </span>
        </div>
        <div style="margin-top: 8px; font-size: 11px; color: #94a3b8; text-align: left; font-weight: 500;">
            📅 {data['date']}
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- 1. ROUND OF 32 ---
with tree_tabs[0]:
    st.subheader("Round of 32 Matches")
    b_left, b_right = st.columns(2, gap="medium")
    
    for count, match_id in enumerate(structural_bracket_flow):
        node = immutable_knockout_tree[match_id]
        active_column = b_left if count < 8 else b_right
        with active_column:
            render_professional_card(match_id, node)


# --- 2. ROUND OF 16 ---
with tree_tabs[1]:
    st.subheader("Round of 16 Bracket Structure")
    r16_c1, r16_c2 = st.columns(2, gap="medium")
    
    r16_tree_map = [
        ("Match 89", "M73", "M77", "July 4"), ("Match 90", "M74", "M78", "July 4"),
        ("Match 93", "M83", "M84", "July 6"), ("Match 94", "M81", "M82", "July 6"),
        ("Match 91", "M75", "M76", "July 5"), ("Match 92", "M79", "M80", "July 5"),
        ("Match 95", "M85", "M86", "July 7"), ("Match 96", "M87", "M88", "July 7")
    ]
    
    for count, (r16_id, left_node, right_node, date_str) in enumerate(r16_tree_map):
        team_left = immutable_knockout_tree[left_node]["winner"] if immutable_knockout_tree[left_node]["winner"] else f"Winner {left_node}"
        team_right = immutable_knockout_tree[right_node]["winner"] if immutable_knockout_tree[right_node]["winner"] else f"Winner {right_node}"
        
        active_column = r16_c1 if count < 4 else r16_c2
        with active_column:
            st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 14px; border-radius: 8px; border: 1px dashed #cbd5e1; margin-bottom: 12px;">
                <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 6px;">🏆 {r16_id} • {date_str}</div>
                <div style="font-size: 13px; font-weight: 600; color: #334155;">⚔️ {team_left} vs {team_right}</div>
            </div>
            """, unsafe_allow_html=True)


# --- 3. QUARTER-FINALS ---
with tree_tabs[2]:
    st.subheader("Quarter-Final Matches (8 Teams)")
    q_c1, q_c2 = st.columns(2, gap="medium")
    
    q_tree_map = [
        ("Match 97", "Match 89", "Match 90", "July 9"), ("Match 98", "Match 93", "Match 94", "July 10"),
        ("Match 99", "Match 91", "Match 92", "July 11"), ("Match 100", "Match 95", "Match 96", "July 11")
    ]
    
    for count, (q_id, left_r16, right_r16, date_str) in enumerate(q_tree_map):
        active_column = q_c1 if count < 2 else q_c2
        with active_column:
            st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 14px; border-radius: 8px; border: 1px dashed #cbd5e1; margin-bottom: 12px;">
                <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 6px;">🏆 {q_id} • {date_str}</div>
                <div style="font-size: 13px; font-weight: 600; color: #334155;">🛡️ Winner {left_r16} vs Winner {right_r16}</div>
            </div>
            """, unsafe_allow_html=True)


# --- 4. SEMI-FINALS & FINAL ---
with tree_tabs[3]:
    col_sf, col_f = st.columns(2, gap="large")
    with col_sf:
        st.markdown("#### 🏟️ Semi-Finals")
        st.markdown("""
        <div style="background-color: #f8fafc; padding: 14px; border-radius: 8px; border: 1px dashed #cbd5e1; margin-bottom: 12px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 6px;">📅 July 14 • Match 101</div>
            <div style="font-size: 13px; font-weight: 600; color: #334155;">🔥 Winner Match 97 vs Winner Match 98</div>
        </div>
        <div style="background-color: #f8fafc; padding: 14px; border-radius: 8px; border: 1px dashed #cbd5e1; margin-bottom: 12px;">
            <div style="font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 6px;">📅 July 15 • Match 102</div>
            <div style="font-size: 13px; font-weight: 600; color: #334155;">🔥 Winner Match 99 vs Winner Match 100</div>
        </div>
        """, unsafe_allow_html=True)
            
    with col_f:
        st.markdown("#### 🥇 Grand Final")
        st.markdown("""
        <div style="background-color: #fff7ed; padding: 18px; border-radius: 8px; border: 2px solid #fed7aa; margin-bottom: 12px;">
            <div style="font-size: 11px; font-weight: 800; color: #c2410c; margin-bottom: 6px;">👑 METLIFE STADIUM • JULY 19</div>
            <div style="font-size: 15px; font-weight: 700; color: #7c2d12;">🏆 Winner Match 101 vs Winner Match 102</div>
        </div>
        """, unsafe_allow_html=True)
