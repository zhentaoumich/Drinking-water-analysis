import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import networkx as nx
import os
import wntr
import folium
from streamlit_folium import st_folium
#
app_title = 'Drinking Water Network Analysis'
app_subtitile = 'Powered by Streamlit and WNTR'

side_bar_text = 'Navigation'
#set layout as wide
st.set_page_config(layout="wide")


#initialization of session state
st.session_state['inp'] = 'data/example.inp'
st.session_state['rpt'] = 'data/example.out'#default path for rpt file
st.session_state['node'] = None
st.session_state['link'] = None
st.session_state['fig_2d'] = None

#create a sidebar
st.sidebar.title(side_bar_text)

uploaded_file = st.sidebar.file_uploader("Choose a EPANET file",type=['inp'])

side_bar_option = st.sidebar.radio('Pages', ['Home', 'Visulization', 'Analysis', 'Simulation', 'Control','About'])



#read epanet file
if uploaded_file is not None:
  
  
   file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
   #st.write(file_details)
  
   with open (os.path.join("data",'uploaded.inp'),'wb') as f:
         f.write(uploaded_file.getbuffer())
  
   temp_file = os.path.join("data",'uploaded.inp')
   inp = wntr.network.WaterNetworkModel(temp_file)
else:
   inp = wntr.network.WaterNetworkModel(st.session_state['inp'])  
#main page
st.title(app_title)  
  
wn_dict = wntr.network.to_dict(inp)

#display the selected option

st.session_state['node'] = pd.DataFrame(wn_dict['nodes'])
st.session_state['link'] = pd.DataFrame(wn_dict['links'])
#convert the selected option to a dataframe


#create x and y columns based on coordinates
st.session_state['node']['x']= st.session_state['node']['coordinates'].apply(lambda x: x[0])
st.session_state['node']['y'] = st.session_state['node']['coordinates'].apply(lambda x: x[1])


#create x and y columns based on coordinates
st.session_state['link']['start_x'] = st.session_state['link']['start_node_name'].apply(lambda x: st.session_state['node'].loc[st.session_state['node']['name'] == x, 'x'].iloc[0])
st.session_state['link']['start_y'] = st.session_state['link']['start_node_name'].apply(lambda x: st.session_state['node'].loc[st.session_state['node']['name'] == x, 'y'].iloc[0])
st.session_state['link']['start_z'] = st.session_state['link']['start_node_name'].apply(lambda x: st.session_state['node'].loc[st.session_state['node']['name'] == x, 'elevation'].iloc[0])
st.session_state['link']['end_x'] = st.session_state['link']['end_node_name'].apply(lambda x: st.session_state['node'].loc[st.session_state['node']['name'] == x, 'x'].iloc[0])
st.session_state['link']['end_y'] = st.session_state['link']['end_node_name'].apply(lambda x: st.session_state['node'].loc[st.session_state['node']['name'] == x, 'y'].iloc[0])
st.session_state['link']['end_z'] = st.session_state['link']['end_node_name'].apply(lambda x: st.session_state['node'].loc[st.session_state['node']['name'] == x, 'elevation'].iloc[0])


def home():

  col1, col2 = st.columns(2)
  with col1:
    #create a dropdown menu
    select_option = st.selectbox('Select an option', ['nodes','links'])#,'options','curves','patterns','sources','controls'])
    st.write('You selected:', select_option)
    if select_option == 'nodes':
      st.dataframe(st.session_state['node'])

    if select_option == 'links':
      st.dataframe(st.session_state['link'])

  with col2:
    fig_2d = go.Figure()
    fig_2d.add_trace(go.Scatter(x=st.session_state['node']['x'], y=st.session_state['node']['y'], 
                            mode='markers',
                            marker=dict(color='grey', size=8),
                            legendgroup='nodes',
                            #name the legend title as nodes
                              name='Nodes'
                            ))
    for index, row in st.session_state['link'].iterrows():
      fig_2d.add_trace(go.Scatter(x=[row['start_x'],row['end_x']], 
                              y=[row['start_y'],row['end_y']], 
                              mode='lines',
                              line=dict(color='green', width=1),
                              legendgroup='links',
                              name = 'Links',
                              showlegend=False
                              ))
    st.session_state['fig_2d'] = fig_2d 
    st.plotly_chart(fig_2d)
  
  return None


def plot_3d():
  
  col1, col2,col3 = st.columns(3)
  #add slide bar for user input
  with col1:
    node_size = st.slider('Node size', min_value=0, max_value=10, value=4, step=1)
  with col2:
    link_size = st.slider('Link size', min_value=0, max_value=10, value=4, step=1)
  with col3:
    z_ratio = st.slider('Z ratio', min_value=0, max_value=10, value=4, step=1)

  fig_3d = go.Figure()
  fig_3d.add_trace(go.Scatter3d(x=st.session_state['node']['x'], y=st.session_state['node']['y'], z=st.session_state['node']['elevation'],
                           mode='markers',
                           marker=dict(color='grey', size=node_size),
                           legendgroup='nodes',
                           #name the legend title as nodes
                            name='Nodes'
                           ))
  for index, row in st.session_state['link'].iterrows():
    fig_3d.add_trace(go.Scatter3d(x=[row['start_x'],row['end_x']], 
                             y=[row['start_y'],row['end_y']], 
                             z=[row['start_z'],row['end_z']], 
                             mode='lines',
                             line=dict(color='green', width=link_size),
                             legendgroup='links',
                             name = 'Links',
                             showlegend=False
                             ))
  #set layout width and height
  fig_3d.update_layout(width=1000, height=800)
  #set z ratio
  fig_3d.update_layout(scene_aspectratio=dict(x=1, y=1, z=z_ratio/10))
  
  st.plotly_chart(fig_3d)
  
  return None

def analysis():
  #add folium base map
  center = [40,-90]
  map = folium.Map(location=center, zoom_start=7)
  st_folium(map, width = 1000, height = 800)
  #add street shp file
  #add building footprint shp file
  #add water network shp file
  #add water network nodes
  #add water network links
  
  
  
  return None

def control():
  
  col1, col2 = st.columns(2)
  with col1:
    st.write('Control model')
    #st.write('Pick a variable to control')
    #add a dropdown menu
    select_option = st.selectbox('Select an node/link', ['nodes','links'])
    if select_option == 'nodes':
      #add a dropdown menu
      id_select_option = st.selectbox('Select id', st.session_state['node']['name'])
      variable_select_option = st.selectbox('Select variable', ['elevation','initial_quality'])
      #write default value
      st.write('Default value:', st.session_state['node'].loc[st.session_state['node']['name'] == id_select_option, variable_select_option].iloc[0])
      
    elif select_option == 'links':
      #add a dropdown menu
      id_select_option = st.selectbox('Select id', st.session_state['link']['name'])
      variable_select_option = st.selectbox('Select variable', ['diameter','length','roughness'])
      #default value
      st.write('Default value:', st.session_state['link'].loc[st.session_state['link']['name'] == id_select_option, variable_select_option].iloc[0])      

    control_value = st.text_input('Control value', '0')
    st.write('', control_value)
    
  
  with col2:
    st.write('Pick a variable to compare')
    select_option2 = st.selectbox('Select an node/link', ['node','link'])
    # if select_option2 == 'node':
    #   #add a dropdown menu
    #   id_select_option2 = st.selectbox('Select id', st.session_state['node']['name'])
    #   variable_select_option2 = st.selectbox('Select variable', ['elevation','initial_quality'])
    #   #write default value
    #   st.write('Default value:', st.session_state['node'].loc[st.session_state['node']['name'] == id_select_option, variable_select_option2].iloc[0])
      
    # elif select_option2 == 'link':
    #   #add a dropdown menu
    #   id_select_option2 = st.selectbox('Select id', st.session_state['link']['name'])
    #   variable_select_option2 = st.selectbox('Select variable', ['diameter','length','roughness','flow'])
    #   #default value
    #   st.write('Default value:', st.session_state['link'].loc[st.session_state['link']['name'] == id_select_option, variable_select_option2].iloc[0])      

  
  return None

if side_bar_option == 'Home':
  home()
elif side_bar_option == 'Visulization':
  plot_3d() 

elif side_bar_option == 'Analysis':
  analysis()
  
elif side_bar_option == 'Simulation':
  #simulation()
  pass

elif side_bar_option == 'Control':
  control()