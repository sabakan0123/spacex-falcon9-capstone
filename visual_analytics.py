"""Build a Folium launch-site map and a small Plotly Dash explorer."""
from pathlib import Path
import pandas as pd
import folium
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / 'dataset_part_2.csv')

def build_map():
    m = folium.Map(location=[32,-98], zoom_start=4, tiles='OpenStreetMap')
    for site, group in df.groupby('LaunchSite'):
        latitude, longitude = group[['Latitude','Longitude']].iloc[0]
        successes = int(group.Class.sum())
        folium.CircleMarker([latitude,longitude],radius=10,color='#00699c',fill=True,
            popup=f'{site}: {successes}/{len(group)} first-stage landing successes',
            tooltip=f'{site}: {len(group)} launches').add_to(m)
    m.save(HERE / 'launch_sites_map.html')

def make_app():
    app=Dash(__name__)
    app.layout=html.Div([
        html.H1('Falcon 9 landing outcomes'),
        html.P('IBM course dataset: 90 launches, 2010–2020'),
        dcc.Dropdown(['All sites']+sorted(df.LaunchSite.unique()),'All sites',id='site'),
        dcc.RangeSlider(0,16000,2000,value=[0,16000],id='payload',tooltip={'placement':'bottom'}),
        html.P(id='count'),dcc.Graph(id='outcomes'),dcc.Graph(id='payload_plot'),
    ],style={'fontFamily':'Arial','maxWidth':'1100px','margin':'auto'})
    @app.callback(Output('count','children'),Output('outcomes','figure'),Output('payload_plot','figure'),Input('site','value'),Input('payload','value'))
    def update(site,payload):
        data=df[df.PayloadMass.between(*payload)]
        if site!='All sites': data=data[data.LaunchSite==site]
        counts=data.Class.map({0:'Unsuccessful / no landing',1:'Successful landing'}).value_counts().rename_axis('Outcome').reset_index(name='Launches')
        pie=px.pie(counts,names='Outcome',values='Launches',title='First-stage outcomes')
        scatter=px.scatter(data,x='PayloadMass',y='FlightNumber',color=data.Class.map({0:'No successful landing',1:'Successful landing'}),hover_data=['LaunchSite','Orbit'],title='Payload and flight number')
        return f'{len(data)} launches match the filters',pie,scatter
    return app

if __name__=='__main__':
    build_map()
    make_app().run(debug=False,host='127.0.0.1',port=8050)
