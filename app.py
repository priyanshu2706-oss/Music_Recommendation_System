import dash
from dash import html, dcc, Output, Input, State
import pandas as pd
import dash_bootstrap_components as dbc

# Load your dataset
df = pd.read_csv("final_music_data_with_spotify_images_fast.csv")

# Map country code to full name
country_mapping = {
    "AE": "United Arab Emirates", "AR": "Argentina", "AT": "Austria", "AU": "Australia",
    "BE": "Belgium", "BG": "Bulgaria", "BO": "Bolivia", "BR": "Brazil", "BY": "Belarus",
    "CA": "Canada", "CH": "Switzerland", "CL": "Chile", "CO": "Colombia", "CR": "Costa Rica",
    "CZ": "Czech Republic", "DE": "Germany", "DK": "Denmark", "DO": "Dominican Republic",
    "EC": "Ecuador", "EE": "Estonia", "EG": "Egypt", "ES": "Spain", "FI": "Finland",
    "FR": "France", "GB": "United Kingdom", "GR": "Greece", "GT": "Guatemala", "HK": "Hong Kong",
    "HN": "Honduras", "HU": "Hungary", "ID": "Indonesia", "IE": "Ireland", "IL": "Israel",
    "IN": "India", "IS": "Iceland", "IT": "Italy", "JP": "Japan", "KR": "South Korea",
    "KZ": "Kazakhstan", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia", "MA": "Morocco",
    "MX": "Mexico", "MY": "Malaysia", "NG": "Nigeria", "NI": "Nicaragua", "NL": "Netherlands",
    "NO": "Norway", "NZ": "New Zealand", "PA": "Panama", "PE": "Peru", "PH": "Philippines",
    "PK": "Pakistan", "PL": "Poland", "PT": "Portugal", "PY": "Paraguay", "RO": "Romania",
    "SA": "Saudi Arabia", "SE": "Sweden", "SG": "Singapore", "SK": "Slovakia", "SV": "El Salvador",
    "TH": "Thailand", "TR": "Turkey", "TW": "Taiwan", "UA": "Ukraine", "US": "United States",
    "UY": "Uruguay", "VE": "Venezuela", "VN": "Vietnam", "ZA": "South Africa"
}

df['country_full'] = df['country'].map(country_mapping)

# Get dropdown values
emotions = sorted(df['emotion'].dropna().unique())
countries = sorted(df['country_full'].dropna().unique())
countries.insert(0, 'All Countries')

# Init Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

app.index_string = '''
<!DOCTYPE html>
<html lang="en">
    <head>
        {%metas%}
        <title>Music Emotion Recommender</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background: linear-gradient(135deg, #001219, #003049);
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                padding: 0;
            }
            .custom-card:hover {
                transform: scale(1.05);
                transition: transform 0.3s ease;
                box-shadow: 0 8px 16px rgba(255, 255, 255, 0.3);
            }
            .custom-card {
                transition: transform 0.3s ease;
                border-radius: 20px;
                overflow: hidden;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .card-img-top {
                height: 400px;
                width: 100%;
                object-fit: cover;
            }
            .card-body {
                display: flex;
                flex-direction: column;
                justify-content: center;
                text-align: center;
                color: white;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = dbc.Container([
    html.H1("🎶 Music Emotion-Based Recommendation", className="text-center text-white mb-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Select Emotion", className="text-white fw-bold"),
            dcc.Dropdown(
                id='emotion-dropdown',
                options=[{'label': e, 'value': e} for e in emotions],
                value='Happy',
                clearable=False
            ),
        ], width=4),

        dbc.Col([
            html.Label("Select Country", className="text-white fw-bold"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': c, 'value': c} for c in countries],
                value='All Countries',
                clearable=False
            ),
        ], width=4),

        dbc.Col([
            html.Label("Select Artist (optional)", className="text-white fw-bold"),
            dcc.Dropdown(id='artist-dropdown', options=[], multi=True, placeholder="Select artist(s)..."),
        ], width=4),
    ], className="mb-4"),

    dbc.Button("🚀 Generate Recommendations", id='generate-button', color='info', className='mb-4 w-100 fw-bold'),

    html.Div(id='recommendation-table')
], fluid=True, style={"padding": "2rem"})


@app.callback(
    Output('artist-dropdown', 'options'),
    Input('country-dropdown', 'value')
)
def update_artist_list(country):
    if country == 'All Countries':
        return []
    filtered = df[df['country_full'] == country]
    unique_artists = sorted(filtered['artists'].dropna().unique())
    return [{'label': artist, 'value': artist} for artist in unique_artists]


@app.callback(
    Output('recommendation-table', 'children'),
    Input('generate-button', 'n_clicks'),
    State('emotion-dropdown', 'value'),
    State('country-dropdown', 'value'),
    State('artist-dropdown', 'value')
)
def update_table(n_clicks, emotion, country, artists):
    if not n_clicks:
        return None

    filtered = df[df['emotion'] == emotion]
    if country != 'All Countries':
        filtered = filtered[filtered['country_full'] == country]
    if artists:
        filtered = filtered[filtered['artists'].isin(artists)]

    filtered = filtered.sort_values(by='popularity', ascending=False)
    filtered = filtered.drop_duplicates(subset=['name', 'artists', 'country_full']).head(20)

    if filtered.empty:
        return html.Div("No songs found!", className="text-danger fw-bold")

    cards = []
    for _, row in filtered.iterrows():
        image = row.get("image_url", "")
        image = image if pd.notna(image) and image != "" else "https://via.placeholder.com/150"

        card = dbc.Col(
            dbc.Card([
                dbc.CardImg(src=image, top=True, className="card-img-top"),
                dbc.CardBody([
                    html.H5(row['name'], className="card-title text-center"),
                    html.P(f"Artist: {row['artists']}", className="card-text text-center"),
                    html.P(f"Country: {row['country_full']}", className="card-text text-center"),
                    html.P(f"Popularity: {row['popularity']}", className="card-text text-center"),
                ])
            ], className="custom-card h-100"),
            width=4, className="mb-4"
        )
        cards.append(card)

    return dbc.Row(cards, className="g-4 justify-content-center")

if __name__ == '__main__':
    app.run(debug=True)