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



def fetch_player_data(country, league, max_retries, timeout_value):
    success = False
    retry_count = 0
    
    while not success and retry_count < max_retries:
        try:
            retry_count += 1
            if retry_count > 1:
                st.info(f"Retry attempt {retry_count}/{max_retries}...")
            
            league_id = countries_leagues[country][league]
            
            
            url = f"https://www.goalserve.com/getfeed/dc097072236e4155927408dd54cd3cd3/soccerleague/{league_id}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive'
            }
            
            st.info(f"Requesting player data with {timeout_value} second timeout...")
            result = requests.get(url, headers=headers, timeout=timeout_value)
            
            if result.status_code == 200:
                st.success("Player data received successfully!")
                
                doc = BeautifulSoup(result.text, "lxml-xml")
                
               
                teams = doc.find_all("team")
                
                if not teams:
                    st.warning("No team data found for this league. The API may have changed its structure.")
                    
                    teams = doc.select("league team") or doc.select("teams team")
                    
                    if not teams:
                        st.error("Could not find team data in the response. Please try another league.")
                        break
                
                players_data = []
                team_names = []
                
                for team in teams:
                    team_info = {}
                    for attr, val in team.attrs.items():
                        team_info[attr] = val
                    
                    team_name = team_info.get('name', 'Unknown')
                    team_names.append(team_name)
                    
                    players = team.find_all("player")
                    if not players:
                        players = team.select("players player")
                    
                    for player in players:
                        player_info = {}
                        player_info['Team-name'] = team_name
                        for attr, value in player.attrs.items():
                            player_info[attr] = value
                        players_data.append(player_info)
                
                if not players_data:
                    st.warning("No player data found. The API structure may have changed.")
                    break
                
                return {
                    "players_data": players_data,
                    "team_names": team_names
                }
                
            else:
                st.error(f"Failed to fetch player data: Status code {result.status_code}")
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
    
    return None



def fetch_fixture_data(country, league, max_retries, timeout_value):
    success = False
    retry_count = 0
    
    while not success and retry_count < max_retries:
        try:
            retry_count += 1
            if retry_count > 1:
                st.info(f"Retry attempt {retry_count}/{max_retries}...")
            
            league_id = countries_leagues[country][league]
            
            
            url = f"https://www.goalserve.com/getfeed/dc097072236e4155927408dd54cd3cd3/soccerfixtures/leagueid/{league_id}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive'
            }
            
            st.info(f"Requesting fixture data with {timeout_value} second timeout...")
            result = requests.get(url, headers=headers, timeout=timeout_value)
            
            if result.status_code == 200:
                st.success("Fixture data received successfully!")
                
                doc = BeautifulSoup(result.text, "lxml-xml")
                
               
                fixtures = []
                
                
                matches = doc.find_all("match") or doc.select("matches match") or doc.select("fixture")
                
                if not matches:
                    st.warning("No fixture data found. The API structure may be different.")
                    
                    return {"fixtures": []}
                
                for match in matches:
                    try:
                        
                        home_team = None
                        away_team = None
                        
                        
                        if match.has_attr('home_name') and match.has_attr('away_name'):
                            home_team = match['home_name']
                            away_team = match['away_name']
                       
                        else:
                            home_elem = match.find('home')
                            away_elem = match.find('away')
                            
                            if home_elem and away_elem:
                                if home_elem.has_attr('name') and away_elem.has_attr('name'):
                                    home_team = home_elem['name']
                                    away_team = away_elem['name']
                                else:
                                    home_name_elem = home_elem.find('name')
                                    away_name_elem = away_elem.find('name')
                                    
                                    if home_name_elem and away_name_elem:
                                        home_team = home_name_elem.text
                                        away_team = away_name_elem.text
                        
                        
                        if not home_team or not away_team:
                            continue
                            
                        
                        match_date = match.get('date', 'Unknown date')
                        match_time = match.get('time', 'Unknown time')
                        match_venue = match.get('venue', 'Unknown venue')
                        
                        
                        if match_venue == 'Unknown venue':
                            venue_elem = match.find('venue')
                            if venue_elem:
                                match_venue = venue_elem.text or venue_elem.get('name', 'Unknown venue')
                        
                        fixture_info = {
                            'home_team': home_team,
                            'away_team': away_team,
                            'date': match_date,
                            'time': match_time,
                            'venue': match_venue
                        }
                        fixtures.append(fixture_info)
                    except Exception as e:
                        st.warning(f"Error extracting fixture details: {str(e)}")
                        continue
                
                return {"fixtures": fixtures}
                
            else:
                st.error(f"Failed to fetch fixture data: Status code {result.status_code}")
                time.sleep(2)
        
        except requests.exceptions.Timeout:
            st.warning(f"Fixture data request timed out (attempt {retry_count}/{max_retries})")
            if retry_count < max_retries:
                st.info(f"Waiting before retry...")
                time.sleep(3)
            else:
                st.error("Maximum retries reached for fixture data.")
        
        except Exception as e:
            st.error(f"An error occurred while fetching fixture data: {str(e)}")
            st.code(traceback.format_exc())
            time.sleep(2)
    
    return {"fixtures": []}



def filter_players_by_teams(players_data, teams):
    return [player for player in players_data if player.get('Team-name') in teams]



if st.sidebar.button("Get League Data"):
    with st.spinner(f"Fetching data for {selected_league} in {selected_country}..."):
        
        player_data_result = fetch_player_data(selected_country, selected_league, max_retries, timeout_value)
        
        if player_data_result:
            
            fixture_data_result = fetch_fixture_data(selected_country, selected_league, max_retries, timeout_value)
            
            
            league_data = {
                "players_data": player_data_result["players_data"],
                "team_names": player_data_result["team_names"],
                "fixtures": fixture_data_result["fixtures"] if fixture_data_result else []
            }
            
           
            st.session_state['league_data'] = league_data
            st.session_state['has_data'] = True



if 'has_data' in st.session_state and st.session_state['has_data']:
    league_data = st.session_state['league_data']
    players_data = league_data['players_data']
    fixtures = league_data['fixtures']
    
    
    players_df = pd.DataFrame(players_data)
    
    tab1, tab2 = st.tabs(["All Players", "Fixtures"])
    
    
    with tab1:
        st.subheader(f"All Players in {selected_league}")
        st.dataframe(players_df)
        
        st.info(f"Total players found: {len(players_df)}")
        
        excel_data = io.BytesIO()
        players_df.to_excel(excel_data, index=False, engine="openpyxl")
        excel_data.seek(0)
        
        st.download_button(
            label="Download Excel File",
            data=excel_data,
            file_name=f"{selected_country}_{selected_league}_players.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    
    with tab2:
        if not fixtures:
            st.warning("No fixture data found for this league. Please check if the fixture API is accessible.")
            
            
            st.subheader("Manual Team Selection")
            st.write("Since fixture data couldn't be retrieved, you can manually select two teams to view their players.")
            
            team_names = league_data['team_names']
            team1 = st.selectbox("Select first team:", team_names)
            team2 = st.selectbox("Select second team:", team_names, index=min(1, len(team_names)-1))
            
            if st.button("Show Players from Selected Teams"):
               
                teams = [team1, team2]
                filtered_players = filter_players_by_teams(players_data, teams)
                filtered_df = pd.DataFrame(filtered_players)
                
                if filtered_df.empty:
                    st.warning(f"No player data found for {teams[0]} and {teams[1]}.")
                else:
                    # Group players by team
                    st.subheader(f"Players from {teams[0]}")
                    team1_df = filtered_df[filtered_df['Team-name'] == teams[0]]
                    st.dataframe(team1_df)
                    
                    st.subheader(f"Players from {teams[1]}")
                    team2_df = filtered_df[filtered_df['Team-name'] == teams[1]]
                    st.dataframe(team2_df)
                    
                    
                    excel_data = io.BytesIO()
                    filtered_df.to_excel(excel_data, index=False, engine="openpyxl")
                    excel_data.seek(0)
                    
                    st.download_button(
                        label="Download Team Players Excel",
                        data=excel_data,
                        file_name=f"{teams[0]}_vs_{teams[1]}_players.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        else:
            st.subheader(f"Fixtures for {selected_league}")
            
            
            fixture_options = [f"{f['home_team']} vs {f['away_team']}" for f in fixtures]
            
            
            fixture_options.insert(0, "Select a fixture")
            
            
            selected_fixture_idx = st.selectbox(
                "Select a fixture to view players from both teams:",
                range(len(fixture_options)),
                format_func=lambda x: fixture_options[x]
            )
            
            
            if selected_fixture_idx > 0:
                fixture = fixtures[selected_fixture_idx - 1]
                
                
                st.write(f"**Date:** {fixture['date']}")
                st.write(f"**Time:** {fixture['time']}")
                if fixture['venue'] != 'Unknown venue':
                    st.write(f"**Venue:** {fixture['venue']}")
                
                
                teams = [fixture['home_team'], fixture['away_team']]
                
                
                filtered_players = filter_players_by_teams(players_data, teams)
                filtered_df = pd.DataFrame(filtered_players)
                
                if filtered_df.empty:
                    st.warning(f"No player data found for {teams[0]} and {teams[1]}.")
                else:
                   
                    st.subheader(f"Players from {teams[0]}")
                    team1_df = filtered_df[filtered_df['Team-name'] == teams[0]]
                    st.dataframe(team1_df)
                    
                    st.subheader(f"Players from {teams[1]}")
                    team2_df = filtered_df[filtered_df['Team-name'] == teams[1]]
                    st.dataframe(team2_df)
                    
                    
                    excel_data = io.BytesIO()
                    filtered_df.to_excel(excel_data, index=False, engine="open")
  



        
        
    
    







