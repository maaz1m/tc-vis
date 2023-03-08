from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

comp_df = pd.read_csv('tc_data.csv')

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


def title():
    return html.H1('TC Visualization App')


def sidebar():
    filter_title = dbc.Label
    year = html.Div([filter_title('Year'), dcc.RangeSlider(2017, 2021, 1, value=[2017, 2021],
                                                           marks={2017: '2017', 2018: '2018', 2019: '2019',
                                                                  2020: '2020', 2021: '2021'}, id='year')])

    title = html.Div([filter_title('Job Title'), dcc.Dropdown(comp_df['title'].dropna().unique(), id='title')])

    tag = html.Div([filter_title('Job Tag'), dcc.Dropdown(comp_df['tag'].dropna().unique(), id='tag')])

    comp = html.Div([filter_title('Compensation'),
                     dcc.Checklist(['basesalary', 'stockgrantvalue', 'bonus'],
                                   ['basesalary', 'stockgrantvalue', 'bonus'], id='comp')])

    exp_type = html.Div([filter_title('Experience Type'),
                         dcc.RadioItems(['yearsofexperience', 'yearsatcompany'], 'yearsofexperience', id='exp_type')])

    exp_min = html.Div(
        [filter_title('Minimum Experience:', md=6), dcc.Input(type='number', id='exp_min', min=0, max=50, step=1)])

    exp_max = html.Div(
        [filter_title('Maximum Experience:', md=6), dcc.Input(type='number', id='exp_max', min=0, max=50, step=1)])

    company = html.Div([filter_title('Company'), dcc.Dropdown(comp_df['company'].dropna().unique(), id='company')])

    location = html.Div([filter_title('Location'), dcc.Dropdown(comp_df['location'].dropna().unique(), id='location')])
    return dbc.Card([
        year, title, tag, comp, exp_type, exp_min, exp_max, company, location, html.Br()
    ], body=True)


def body():
    histogram_tab = dbc.Tab(label='Distribution', children=[
        dcc.Graph(id='histogram')
    ])

    pie_tab = dbc.Tab(label='Breakdown', children=[
        dcc.Graph(id='pie')
    ])

    boxplot_tab = dbc.Tab(label='Top Tags', children=[
        dcc.Graph(id='boxplot')
    ])

    parcat_tab = dbc.Tab(label='Tag and Titles', children=[
        dcc.Graph(id='parcat')
    ])

    scatter_tab = dbc.Tab(label='Top Locations', children=[
        dcc.Graph(id='scatter')
    ])

    line_tab = dbc.Tab(label='Company Growth', children=[
        dcc.Graph(id='line')
    ])

    return dbc.Tabs([
        histogram_tab,
        pie_tab,
        boxplot_tab,
        parcat_tab,
        scatter_tab,
        line_tab
    ], id='body')


def aggregate(df, col, n):
    medians = df.groupby([col]).median()
    means = df.groupby([col]).mean()
    sizes = df.groupby([col]).size()
    top = sizes.nlargest(n).index
    is_top = sizes.index.isin(top)

    return pd.DataFrame({
        col: top,
        'compensation': medians[is_top]['compensation'],
        'experience': means[is_top]['experience'],
        'size': sizes[is_top]
    })


@app.callback(
    Output(component_id='histogram', component_property='figure'),
    Output(component_id='boxplot', component_property='figure'),
    Output(component_id='scatter', component_property='figure'),
    Output(component_id='parcat', component_property='figure'),
    Output(component_id='line', component_property='figure'),
    Output(component_id='pie', component_property='figure'),
    [Input(component_id=filter_id, component_property='value') for filter_id in
     ['year', 'title', 'tag', 'comp', 'exp_type', 'exp_min', 'exp_max', 'company', 'location']]
)
def update(year, title, tag, comp, exp_type, exp_min, exp_max, company, location):
    filters = comp_df['year'].between(year[0], year[1]) & \
              (1 if title is None else comp_df['title'] == title) & \
              (1 if tag is None else comp_df['tag'] == tag) & \
              (1 if exp_min is None else comp_df[exp_type] >= exp_min) & \
              (1 if exp_max is None else comp_df[exp_type] <= exp_max) & \
              (1 if company is None else comp_df['company'] == company) & \
              (1 if location is None else comp_df['location'] == location)

    comp_df['compensation'] = sum([comp_df[c] for c in comp])
    comp_df['experience'] = comp_df[exp_type]
    comp_df_f = comp_df[filters]

    histogram = px.histogram(comp_df_f, x='compensation', color_discrete_sequence=['indianred'], marginal='box')

    top_tags = list(comp_df_f['tag'].value_counts().head(12).index)
    is_top_tag = comp_df_f['tag'].isin(top_tags)
    boxplot = px.box(comp_df_f[is_top_tag], y='tag', x='compensation',
                     color_discrete_sequence=px.colors.qualitative.G10)

    location_agg = aggregate(comp_df_f, 'location', 20)
    scatter = px.scatter(location_agg, x='experience', y='compensation', size='size', hover_name='location',
                         color='location')

    top_titles = list(comp_df_f['title'].value_counts().head(12).index)
    is_top_title = comp_df_f['title'].isin(top_titles)
    parcat = px.parallel_categories(comp_df_f[is_top_title & is_top_tag], dimensions=['title', 'tag'])

    top_companies = list(comp_df_f['company'].value_counts().head(6).index)
    is_top_company = comp_df_f['company'].isin(top_companies)
    company_experience_agg = comp_df_f[is_top_company].groupby(['company', 'experience']).median()[
        'compensation'].reset_index()
    line = px.scatter(company_experience_agg, x='experience', y='compensation', color='company', trendline='ols')

    pie = px.pie(pd.melt(comp_df_f, value_vars=comp, var_name='compensation type'), values='value',
                 names='compensation type')

    return histogram, boxplot, scatter, parcat, line, pie
