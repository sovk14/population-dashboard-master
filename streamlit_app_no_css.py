# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

# Load data
df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')

# Sidebar
with st.sidebar:
    st.title('🏂 US Population Dashboard')
    
    year_list = list(df_reshaped.year.unique())[::-1]
    selected_year = st.selectbox('Select a year', year_list)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

# Function to calculate inbound and outbound migration data
def calculate_migration_data(input_df, selected_year):
    selected_year_data = input_df[input_df['year'] == selected_year].reset_index()
    previous_year_data = input_df[input_df['year'] == selected_year - 1].reset_index()

    selected_year_data['population_difference'] = selected_year_data.population - previous_year_data.population
    selected_year_data['inbound_migration'] = selected_year_data['population_difference'].where(selected_year_data['population_difference'] > 0, 0)
    selected_year_data['outbound_migration'] = -selected_year_data['population_difference'].where(selected_year_data['population_difference'] < 0, 0)

    return selected_year_data[['states', 'inbound_migration', 'outbound_migration']]

# Function to create a scatter plot
def make_scatter_plot(input_df):
    scatter_plot = alt.Chart(input_df).mark_circle(size=60).encode(
        x=alt.X('inbound_migration:Q', title='Inbound Migration'),
        y=alt.Y('outbound_migration:Q', title='Outbound Migration'),
        color='states:N',
        tooltip=['states:N', 'inbound_migration:Q', 'outbound_migration:Q']
    ).properties(
        title='Inbound vs Outbound Migration by State',
        width=900,
        height=400
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )
    
    return scatter_plot

# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Gains/Losses')

    df_population_difference_sorted = calculate_migration_data(df_reshaped, selected_year)

    if selected_year > 2010:
        first_state_name = df_population_difference_sorted.states.iloc[0]
        first_state_population = df_selected_year_sorted.population.iloc[0]
        first_state_delta = df_population_difference_sorted.inbound_migration.iloc[0]
    else:
        first_state_name = '-'
        first_state_population = '-'
        first_state_delta = ''
    st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

    if selected_year > 2010:
        last_state_name = df_population_difference_sorted.states.iloc[-1]
        last_state_population = df_selected_year_sorted.population.iloc[-1]   
        last_state_delta = df_population_difference_sorted.outbound_migration.iloc[-1]   
    else:
        last_state_name = '-'
        last_state_population = '-'
        last_state_delta = ''
    st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)

with col[1]:
    st.markdown('#### Migration Patterns')

    df_migration_data = calculate_migration_data(df_reshaped, selected_year)

    scatter_plot = make_scatter_plot(df_migration_data)
    st.altair_chart(scatter_plot, use_container_width=True)

with col[2]:
    st.markdown('#### Top States')

    st.dataframe(df_selected_year_sorted,
                 column_order=("states", "population"),
                 hide_index=True,
                 column_config={
                    "states": st.column_config.TextColumn(
                        "States",
                    ),
                    "population": st.column_config.ProgressColumn(
                        "Population",
                        format="%f",
                        min_value=0,
                        max_value=max(df_selected_year_sorted.population),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).
            - :orange[**Gains/Losses**]: states with high inbound/ outbound migration for selected year.
            - :orange[**Migration Patterns**]: scatter plot showing the relationship between inbound and outbound migration.
            ''')

