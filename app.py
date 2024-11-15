import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Load the logo using the specified path
logo = Image.open("D:/streamlit/logo.webp")

# Display the logo and title in Streamlit
st.image(logo, width=100)  # Adjust width as needed
st.title("Football Match Day Interactive Dashboard")

# Project Description
st.markdown("""
    This dashboard provides an interactive way to analyze football matches, focusing on match day statistics, 
    team performance, and visual representations of goals, fouls, and other insights. 
    You can filter the data by league, team, and date range to get a comprehensive view of football statistics 
    and team comparisons. Additionally, this dashboard highlights the top-scoring teams in the selected league.
""")

# Load the match day data
@st.cache_data
def load_data():
    data = pd.read_excel("match_data.xlsx", sheet_name="Sheet1")
    data['Date'] = pd.to_datetime(data['Date'])  # Ensure date is in the right format
    return data

# Load the data
df = load_data()

# Sidebar filters with expander
st.sidebar.header("Filters")
with st.sidebar.expander("Select League and Teams", expanded=True):
    # League filter
    selected_league = st.selectbox("🏆 Select League", df['League'].unique(), index=0)

    # Team filter: allows selection of two teams for comparison
    league_teams = df[df['League'] == selected_league]
    available_teams = pd.concat([league_teams['HomeTeam'], league_teams['AwayTeam']]).unique()
    selected_team1 = st.selectbox("⚽ Select Team 1", available_teams, index=0)
    selected_team2 = st.selectbox("⚽ Select Team 2 (optional)", ["None"] + list(available_teams))

    # Date range filter
    date_range = st.date_input("📅 Select Date Range", [df['Date'].min().date(), df['Date'].max().date()])
    date_range = [pd.to_datetime(date) for date in date_range]

# Filter data based on selections for team 1
filtered_df1 = df[
    ((df['HomeTeam'] == selected_team1) | (df['AwayTeam'] == selected_team1)) &
    (df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])
]

# Filter data for team 2 if selected
filtered_df2 = None
if selected_team2 != "None":
    filtered_df2 = df[
        ((df['HomeTeam'] == selected_team2) | (df['AwayTeam'] == selected_team2)) &
        (df['Date'] >= date_range[0]) & (df['Date'] <= date_range[1])
    ]

# Display filtered data for team(s)
st.subheader("📊 Filtered Match Data")

col1, col2 = st.columns(2)
with col1:
    st.write(f"**Match Data for {selected_team1}**")
    st.write(filtered_df1)

if filtered_df2 is not None:
    with col2:
        st.write(f"**Match Data for {selected_team2}**")
        st.write(filtered_df2)

# Function to calculate match insights for a specific team
def calculate_insights(filtered_df, team):
    total_goals = filtered_df[filtered_df['HomeTeam'] == team]['HomeGoals'].sum() + \
                  filtered_df[filtered_df['AwayTeam'] == team]['AwayGoals'].sum()
    total_matches = len(filtered_df)
    avg_goals_per_match = total_goals / total_matches if total_matches > 0 else 0
    total_fouls = filtered_df[filtered_df['HomeTeam'] == team]['HomeFouls'].sum() + \
                  filtered_df[filtered_df['AwayTeam'] == team]['AwayFouls'].sum()
    wins = len(filtered_df[(filtered_df['HomeTeam'] == team) & (filtered_df['HomeGoals'] > filtered_df['AwayGoals'])]) + \
           len(filtered_df[(filtered_df['AwayTeam'] == team) & (filtered_df['AwayGoals'] > filtered_df['HomeGoals'])])
    losses = len(filtered_df[(filtered_df['HomeTeam'] == team) & (filtered_df['HomeGoals'] < filtered_df['AwayGoals'])]) + \
             len(filtered_df[(filtered_df['AwayTeam'] == team) & (filtered_df['AwayGoals'] < filtered_df['HomeGoals'])])
    draws = total_matches - wins - losses
    clean_sheets = len(filtered_df[((filtered_df['HomeTeam'] == team) & (filtered_df['AwayGoals'] == 0)) | 
                                   ((filtered_df['AwayTeam'] == team) & (filtered_df['HomeGoals'] == 0))])
    return {
        "Total Matches": total_matches,
        "Wins": wins,
        "Losses": losses,
        "Draws": draws,
        "Clean Sheets": clean_sheets,
        "Total Goals Scored": total_goals,
        "Average Goals per Match": round(avg_goals_per_match, 2),
        "Total Fouls": total_fouls
    }

# Display match insights side-by-side
st.subheader("📈 Match Insights Comparison")

col1, col2 = st.columns(2)
insights1 = calculate_insights(filtered_df1, selected_team1)
with col1:
    st.write(f"**Insights for {selected_team1}**")
    for key, value in insights1.items():
        st.metric(label=key, value=value)

if filtered_df2 is not None:
    insights2 = calculate_insights(filtered_df2, selected_team2)
    with col2:
        st.write(f"**Insights for {selected_team2}**")
        for key, value in insights2.items():
            st.metric(label=key, value=value)




# Head-to-Head Comparison (calculations outside the conditional block)
team1_wins = None
team2_wins = None
draws = None

if selected_team1 != "None" and selected_team2 != "None":
    st.subheader("Head-to-Head Comparison")

    head_to_head_data = df[
        ((df['HomeTeam'] == selected_team1) & (df['AwayTeam'] == selected_team2)) |
        ((df['HomeTeam'] == selected_team2) & (df['AwayTeam'] == selected_team1))
    ]

    team1_wins = len(head_to_head_data[(head_to_head_data['HomeTeam'] == selected_team1) & (head_to_head_data['HomeGoals'] > head_to_head_data['AwayGoals'])]) + \
                len(head_to_head_data[(head_to_head_data['AwayTeam'] == selected_team1) & (head_to_head_data['AwayGoals'] > head_to_head_data['HomeGoals'])])

    team2_wins = len(head_to_head_data[(head_to_head_data['HomeTeam'] == selected_team2) & (head_to_head_data['HomeGoals'] > head_to_head_data['AwayGoals'])]) + \
                len(head_to_head_data[(head_to_head_data['AwayTeam'] == selected_team2) & (head_to_head_data['AwayGoals'] > head_to_head_data['HomeGoals'])])

    draws = len(head_to_head_data[head_to_head_data['HomeGoals'] == head_to_head_data['AwayGoals']])

    total_matches = len(head_to_head_data)
    team1_losses = total_matches - team1_wins - draws
    team2_losses = total_matches - team2_wins - draws
# Create a bar chart
fig, ax = plt.subplots()
labels = [selected_team1, selected_team2]
wins = [team1_wins, team2_wins]
losses = [team1_losses, team2_losses]
draws = [draws, draws]

x = np.arange(len(labels))
width = 0.2

rects1 = ax.bar(x - width, wins, width, label='Wins')
rects2 = ax.bar(x, draws, width, label='Draws')
rects3 = ax.bar(x + width, losses, width, label='Losses')

# Add labels above the bars
ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)
ax.bar_label(rects3, padding=3)

ax.set_ylabel('Count')
ax.set_title('Head-to-Head Comparison')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

st.pyplot(fig)


# Visualizations: Goals and Fouls Comparison for Team 1 and Team 2
st.subheader("🔍 Goals and Fouls Comparison")

# Goals Comparison
col1, col2 = st.columns(2)

with col1:
    if not filtered_df1.empty:
        fig, ax = plt.subplots()
        home_goals1 = filtered_df1[filtered_df1['HomeTeam'] == selected_team1]['HomeGoals'].sum()
        away_goals1 = filtered_df1[filtered_df1['AwayTeam'] == selected_team1]['AwayGoals'].sum()
        ax.bar(['Home Goals', 'Away Goals'], [home_goals1, away_goals1], color=['#1f77b4', '#ff7f0e'])
        ax.set_title(f"{selected_team1} Goals (Bar Chart)")
        ax.set_ylabel("Goals")
        ax.set_ylim(0, max(home_goals1, away_goals1) + 1)  # Dynamic y-axis limit
        st.pyplot(fig)
    else:
        st.write(f"No data available for {selected_team1}.")

if filtered_df2 is not None:
    with col2:
        if not filtered_df2.empty:
            fig, ax = plt.subplots()
            home_goals2 = filtered_df2[filtered_df2['HomeTeam'] == selected_team2]['HomeGoals'].sum()
            away_goals2 = filtered_df2[filtered_df2['AwayTeam'] == selected_team2]['AwayGoals'].sum()
            ax.bar(['Home Goals', 'Away Goals'], [home_goals2, away_goals2], color=['#1f77b4', '#ff7f0e'])
            ax.set_title(f"{selected_team2} Goals (Bar Chart)")
            ax.set_ylabel("Goals")
            ax.set_ylim(0, max(home_goals2, away_goals2) + 1)  # Dynamic y-axis limit
            st.pyplot(fig)
        else:
            st.write(f"No data available for {selected_team2}.")

# Pie Chart for Fouls Comparison
st.subheader("⚖️ Fouls Comparison (Pie Chart)")

col1, col2 = st.columns(2)

with col1:
    if not filtered_df1.empty:
        fig, ax = plt.subplots()
        home_fouls1 = filtered_df1[filtered_df1['HomeTeam'] == selected_team1]['HomeFouls'].sum()
        away_fouls1 = filtered_df1[filtered_df1['AwayTeam'] == selected_team1]['AwayFouls'].sum()
        ax.pie([home_fouls1, away_fouls1], labels=['Home Fouls', 'Away Fouls'], autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff'])
        ax.set_title(f"{selected_team1} Fouls (Pie Chart)")
        st.pyplot(fig)
    else:
        st.write(f"No data available for {selected_team1}.")

if filtered_df2 is not None:
    with col2:
        if not filtered_df2.empty:
            fig, ax = plt.subplots()
            home_fouls2 = filtered_df2[filtered_df2['HomeTeam'] == selected_team2]['HomeFouls'].sum()
            away_fouls2 = filtered_df2[filtered_df2['AwayTeam'] == selected_team2]['AwayFouls'].sum()
            ax.pie([home_fouls2, away_fouls2], labels=['Home Fouls', 'Away Fouls'], autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff'])
            ax.set_title(f"{selected_team2} Fouls (Pie Chart)")
            st.pyplot(fig)
        else:
            st.write(f"No data available for {selected_team2}.")

# Top Scoring Teams Visualization
if selected_league:
    st.subheader(f"🏆 Top Scoring Teams in the {selected_league} within the selected date range")

    # Filter data based on selected league and date range
    filtered_league_data = df[(df['League'] == selected_league) &
                               (df['Date'] >= date_range[0]) &
                               (df['Date'] <= date_range[1])]

    # Calculate total goals for each team in the filtered data
    total_goals = filtered_league_data.groupby('HomeTeam')['HomeGoals'].sum().reset_index()
    away_goals = filtered_league_data.groupby('AwayTeam')['AwayGoals'].sum().reset_index()

    total_goals = total_goals.rename(columns={'HomeTeam': 'Team', 'HomeGoals': 'TotalGoals'})
    away_goals = away_goals.rename(columns={'AwayTeam': 'Team', 'AwayGoals': 'TotalGoals'})

    # Merge home and away goals
    total_goals = pd.concat([total_goals, away_goals]).groupby('Team', as_index=False).sum()
    top_scorers = total_goals.nlargest(6, 'TotalGoals')

    # Display top scorers
    st.write("### Top 6 Scoring Teams")
  

    # Bar chart for top scoring teams
    fig, ax = plt.subplots()
    ax.bar(top_scorers['Team'], top_scorers['TotalGoals'], color='green')
    ax.set_xlabel("Teams")
    ax.set_ylabel("Total Goals")
    ax.set_title(f"Top 6 Scoring Teams in the {selected_league}")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Footer
st.markdown("""
    ---
    &copy; 2024 Vaibhav Magdum. All rights reserved.
""")
