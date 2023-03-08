# app.py

from dash import html
from components import app, title, sidebar, body
import dash_bootstrap_components as dbc

app.layout = dbc.Container([
    title(),
    html.Hr(),
    dbc.Row([
        dbc.Col(sidebar(), md=4),
        dbc.Col(body(), md=8, align='top')
    ],
        align='center'
    )
], fluid=True)


if __name__ == '__main__':
    app.run()
