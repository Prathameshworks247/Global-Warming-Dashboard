import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shiny.express import ui, input, render
from shiny import reactive
from pathlib import Path
import pycountry
import seaborn as sns
import folium 
from folium import plugins



ui.page_opts(fillable = True )

def get_country_iso3(country_name):
    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_3
    except LookupError:
        return None


#data 1

directory = Path(__file__).parent
modified_temp_city = pd.read_csv('modified_temp_city.csv')



#data 2
global_temp_country = pd.read_csv(f'{directory}/dataframes/GlobalLandTemperaturesByCountry.csv')
global_temp_country = global_temp_country.dropna()
global_temp_country['dt'] = global_temp_country['dt'].str[:4]
df_temp2 = global_temp_country.groupby(["Country","dt"])["AverageTemperature"].mean().reset_index()
df_temp2['dt'] = df_temp2['dt'].astype(int)
df_temp2['ISO'] = df_temp2['Country'].apply(lambda x: get_country_iso3(x))

#data3
@reactive.calc
def dat():
    return modified_temp_city

@reactive.calc
def countrywise_dat():
    if input.country() == 'World':
        df_temp3_temp = modified_temp_city
    else:
        df_temp3_temp = modified_temp_city[modified_temp_city['Country'] == input.country()]
    if input.Climate() == "Continental":
        df_temp3_temp = df_temp3_temp[(df_temp3_temp['AverageTemperature']<15) & (df_temp3_temp['AverageTemperature']>5)]
    if input.Climate() == "Polar":
        df_temp3_temp = df_temp3_temp[(df_temp3_temp['AverageTemperature']<0 )& (df_temp3_temp['AverageTemperature']>-40)]
    if input.Climate() == "Arid":
        df_temp3_temp = df_temp3_temp[(df_temp3_temp['AverageTemperature']<22) & (df_temp3_temp['AverageTemperature']>15)]
    return df_temp3_temp

@reactive.calc
def countrywise_dat2():
    if input.country() == 'World':
        return df_temp2
    else:
        df_temp2_temp = df_temp2[df_temp2['Country'] == input.country()]
        return df_temp2_temp.reset_index()


with ui.layout_sidebar():
    with ui.sidebar(open="open"):
        ui.input_select("country", "Select a country",[
    "World", "United States", "Canada", "United Kingdom", "Germany", "France", "Australia", 
    "Japan", "India", "China", "Russia", "Brazil", "Mexico", "Italy", "Spain", 
    "South Korea", "Netherlands", "Turkey", "Saudi Arabia", "South Africa", 
    "Argentina", "Egypt", "Sweden", "Switzerland", "Poland", "Belgium", 
    "Norway", "Austria", "Denmark", "Finland", "Ireland", "New Zealand", 
    "Singapore", "Thailand", "Israel", "United Arab Emirates", "Greece", 
    "Portugal", "Hungary", "Czech Republic", "Romania", "Colombia", 
    "Chile", "Peru", "Vietnam", "Philippines", "Malaysia", 
    "Pakistan", "Indonesia", "Iran", "Nigeria"
    ])      
        ui.input_select("Climate", "Sort by climate", ["---","Continental", "Arid", "Polar"])
        
    with ui.card():
        "Average temperature of countries over the years"
        @render.plot
        def show_plot():
            df = countrywise_dat2()
            plt.title("Selected country's average temperature trajectory over the years.")
            ax = sns.lineplot(x='dt', y='AverageTemperature', data=df)
            mean_temp = df['AverageTemperature'].mean()
            ax.set_ylim(mean_temp - 5, mean_temp + 5)

    with ui.card():
        "Heatmap of temperature in different cities."
        @render.ui
        def show_heatmap():
            df = countrywise_dat()
            m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=4)
            heat_data = [[row['Latitude'], row['Longitude'], row['AverageTemperature']] for index, row in df.iterrows()]
            plugins.HeatMap(heat_data).add_to(m)
            return m


    @render.data_frame
    def data1():
        return countrywise_dat().head(100)
    
    