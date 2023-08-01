from dash import Dash, html
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from pages import start_trial
from pages import current_exp

#como pestañas las posibles páginas? 
children_pages=[
    *[
    dbc.NavItem(dbc.NavLink(page["name"], 
        href=page["path"]), 
        className="nav-item",)
            for page in dash.page_registry.values() 
                if page["module"] != "pages.not_found_404" 
    ],   
]

children_fixed = [
                dbc.NavItem(dbc.NavLink('Page 1',href='/page-1')),
                dbc.NavItem(dbc.DropdownMenu(nav=True,
                    in_navbar=True, 
                    id='dropdown',
                    label='more',
                    children = [
                        dbc.DropdownMenuItem('Page 2',href='/page-2'),
                        dbc.DropdownMenuItem('Page 3',href='/page-3'),
                    ],
                ) )
            ]



def get_navbar():
    nv = dbc.NavbarSimple(id = "navbar",
            children = children_pages,#children_fixed,
            brand='NombreApp',
            brand_href='#', #link a algo?
            className="navbar",
            #esto es estilo debería ir en el css
            color='secondary',
            dark=True,
            style={"margin": False}  ,
        )
    return nv

def get_layout():
    
    layout = html.Div([
        get_navbar(),        
        dash.page_container,
        
    ])
    return layout