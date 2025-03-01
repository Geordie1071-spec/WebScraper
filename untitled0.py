import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import time
import traceback


st.title("Soccer League Player Data Scraper")


countries_leagues = {
    "England": {
        "Premier League": "1204",
        "Championship": "1205",
        "League One": "1206"
    },
    "Spain": {
        "La Liga": "1399",
        "La Liga 2": "1398"
    },
    "Germany": {
        "Bundesliga": "1229",
        "2. Bundesliga": "1225"
    },
    "Italy": {
        "Serie A": "1269",
        "Serie B": "1265"
    },
    "France": {
        "Ligue 1": "1221",
        "Ligue 2": "1217"
    },
    "Turkey": {
        "Super Lig": "1425"
    },
    "UEFA": {
        "Champions League": "1005",
        "Europa": "1007",
        "Conference": "18853"
    },
    "Holland": {
        "Eredivisie": "1322"
    },
    "Portugal": {
        "Liga": "1352"
    },
    "Argentina": {
        "Liga Professional": "1081"
    },
    "Brazil": {
        "SerieA": "1141"
    },
    "Saudi Arabia": {
        "Professional League": "1368"
    },
    "Poland": {
        "Ekstraklasa": "1344"
    },
    "Scotland": {
        "Premiership": "1370"
    },
    "Australia": {
        "A League": "1086"
    },
    "USA": {
        "MLS": "1440"
    },
    "Mexico": {
        "MX Liga": "1308"
    },
    "Colombia": {
        "Primera A": "1167"
    },
    "Japan": {
        "J1 League": "1271"
    },
    "China": {
        "Super League": "1163"
    },
    "Sweden": {
        "Allsvenskan": "1407"
    },
    "Denmark": {
        "Superliga": "1185"
    },
    "Belgium": {
        "Pro Jupiler": "1104"
    },
    "South Korea": {
        "K League": "1282"
    }
}


st.sidebar.header("Select Country and League")


selected_country = st.sidebar.selectbox(
    "Select Country",
    options=list(countries_leagues.keys())
)


selected_league = st.sidebar.selectbox(
    "Select League",
    options=list(countries_leagues[selected_country].keys())
)


max_retries = st.sidebar.slider("Max Retries", min_value=1, max_value=5, value=3)
timeout_value = st.sidebar.slider("Timeout (seconds)", min_value=5, max_value=60, value=30)


if st.sidebar.button("Get Player Data"):
    
    with st.spinner(f"Fetching player data for {selected_league} in {selected_country}..."):
        success = False
        retry_count = 0
        
        while not success and retry_count < max_retries:
            try:
                retry_count += 1
                if retry_count > 1:
                    st.info(f"Retry attempt {retry_count}/{max_retries}...")
                
                
                league_id = countries_leagues[selected_country][selected_league]
                
                
                url = f"https://www.goalserve.com/getfeed/dc097072236e4155927408dd54cd3cd3/soccerleague/{league_id}"
                
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection': 'keep-alive'
                }
                
                
                st.info(f"Requesting data with {timeout_value} second timeout...")
                result = requests.get(url, headers=headers, timeout=timeout_value)
                
                
                if result.status_code == 200:
                    st.success("Data received successfully!")
                    
                   
                    doc = BeautifulSoup(result.text, "lxml-xml")
                    
                    
                    teams = doc.find_all("team")
                    
                    if not teams:
                        st.warning("No team data found for this league. The API may have changed its structure.")
                        
                        
                        st.info("Trying alternate data structure...")
                        
                        teams = doc.select("league team") or doc.select("teams team")
                        
                        if not teams:
                            st.error("Could not find team data in the response. Please try another league.")
                            break
                    
                    
                    players_data = []
                    for team in teams:
                        team_info = {}
                        for attr, val in team.attrs.items():
                            team_info[attr] = val
                        
                        
                        players = team.find_all("player")
                        if not players:
                            players = team.select("players player")
                        
                        for player in players:
                            player_info = {}
                            player_info['Team-name'] = team_info.get('name', 'Unknown')
                            for attr, value in player.attrs.items():
                                player_info[attr] = value
                            players_data.append(player_info)
                    
                    if not players_data:
                        st.warning("No player data found. The API structure may have changed.")
                        break
                    
                    
                    df = pd.DataFrame(players_data)
                    
                    
                    st.subheader(f"Player Data for {selected_league}")
                    st.dataframe(df.head(10))
                    
                   
                    st.info(f"Total players found: {len(df)}")
                    
                    
                    excel_data = io.BytesIO()
                    df.to_excel(excel_data, index=False, engine="openpyxl")
                    excel_data.seek(0)
                    
                    st.download_button(
                        label="Download Excel File",
                        data=excel_data,
                        file_name=f"{selected_country}_{selected_league}_players.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    success = True
                else:
                    st.error(f"Failed to fetch data: Status code {result.status_code}")
                    time.sleep(2)  
            
            except requests.exceptions.Timeout:
                st.warning(f"Request timed out (attempt {retry_count}/{max_retries})")
                if retry_count < max_retries:
                    st.info(f"Waiting before retry...")
                    time.sleep(3)  
                else:
                    st.error("Maximum retries reached. The API server is not responding in time.")
                    st.info("""
                    Troubleshooting tips:
                    1. Try increasing the timeout value in the sidebar
                    2. Try a different league or country
                    3. The API key might be expired or restricted
                    4. The Goalserve server might be experiencing issues
                    """)
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.code(traceback.format_exc())
                time.sleep(2)  


st.sidebar.markdown("---")
st.sidebar.info("""
This app scrapes player data from the Goalserve API.
If you encounter timeout errors, try:
1. Increasing the timeout value
2. Reducing the number of retries
3. Trying a different league
""")


if 'df' not in locals():
    st.markdown("""
    ## Instructions
    1. Select a country from the sidebar
    2. Choose a league from that country
    3. Adjust timeout and retry settings if needed
    4. Click "Get Player Data" to retrieve the information
    5. Preview the data and download as Excel
    """)
    
    st.info("""
    Note: The Goalserve API might be slow to respond or may have access restrictions.
    If you continue to have issues, you might need to:
    
    1. Check if the API key in the URL is still valid
    2. Try accessing the data at a different time
    3. Contact Goalserve to verify your access permissions
    """)
  



        
        
    
    







