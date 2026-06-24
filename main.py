from fastapi import FastAPI
from scraper import scrape_matches

app = FastAPI(
    title="FIFA World Cup 2026 API",
    description="Live web scraping API for tracking World Cup 2026 match results from Wikipedia",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Welcome to the World Cup 2026 API",
        "endpoints": {
            "all_matches": "/matches",
            "filter_by_team": "/matches/{team_name}",
            "documentation": "/docs"
        }
    }

@app.get("/matches")
def get_matches():
    live_data = scrape_matches()
    return {
        "status": "success",
        "total_matches": len(live_data),
        "data": live_data
    }

@app.get("/matches/{team_name}")
def get_matches_by_team(team_name: str):
    live_data = scrape_matches()
    
    filtered_matches = [
        match for match in live_data 
        if team_name.lower() in match["home_team"].lower() or team_name.lower() in match["away_team"].lower()
    ]
    
    return {
        "status": "success",
        "team_searched": team_name,
        "total_found": len(filtered_matches),
        "data": filtered_matches
    }