# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 11:47:16 2022

@author: dell
"""


import streamlit as st
import pandas as pd
import numpy as np
import plotly as px
from  PIL import Image
import io 
from st_aggrid import AgGrid

pd.read_csv(r'./C__Users_chlox_Documents_stream.csv')
uploaded_file = st.file_uploader("Fill out the project plan template and upload your file here. After you upload the file, you can edit your project plan within the app.", type=['csv'])



if uploaded_file is not None:
    Tasks=pd.read_csv(uploaded_file)
    Tasks['Start'] = Tasks['Start'].astype('datetime64')
    Tasks['End'] = Tasks['End'].astype('datetime64')
    
    grid_response = AgGrid(
        Tasks,
        editable=True, 
        height=300, 
        width='100%',
        )

    updated = grid_response['data']
    df = pd.DataFrame(updated) 
    

    st.title("GANTT Chart")

    st.markdown('''
    This is a GANTT chart informing about periods of *automatic/manual* operations''')
    
    if st.button('Generate Gantt Chart'): 
        fig = px.express.timeline(
                        df, 
                        x_start="Start", 
                        x_end="End", 
                        y="Mode",
                        color="Mode",
                        hover_name="Mode"
                        )

        fig.update_yaxes(autorange="reversed")          #if not specified as 'reversed', the tasks will be listed from bottom up       
        
        fig.update_layout(
                        title='Project Plan Gantt Chart',
                        hoverlabel_bgcolor='#DAEEED',   #Change the hover tooltip background color to a universal light blue color. If not specified, the background color will vary by team or completion pct, depending on what view the user chooses
                        bargap=0.2,
                        height=600,              
                        xaxis_title="", 
                        yaxis_title="",                   
                        title_x=0.5,                    #Make title centered                     
                        xaxis=dict(
                                tickfont_size=15,
                                tickangle = 270,
                                rangeslider_visible=True,
                                side ="top",            #Place the tick labels on the top of the chart
                                showgrid = True,
                                zeroline = True,
                                showline = True,
                                showticklabels = True,
                                tickformat="%x\n",      #Display the tick labels in certain format. To learn more about different formats, visit: https://github.com/d3/d3-format/blob/main/README.md#locale_format
                                )
                    )
        
        fig.update_xaxes(tickangle=0, tickfont=dict(family='Rockwell', color='blue', size=15))

        st.plotly_chart(fig, use_container_width=True)  #Display the plotly chart in Streamlit

        st.subheader('Bonus: Export the interactive Gantt chart to HTML and share with others!') #Allow users to export the Plotly chart to HTML
        buffer = io.StringIO()
        fig.write_html(buffer, include_plotlyjs='cdn')
        html_bytes = buffer.getvalue().encode()
        st.download_button(
            label='Export to HTML',
            data=html_bytes,
            file_name='Gantt.html',
            mime='text/html'
        ) 
    else:
        st.write('---') 
   
else:
    st.warning('You need to upload a csv file.')





