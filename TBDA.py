# -*- coding: utf-8 -*-

######## - Importations - ########

from datetime import datetime,date,time,timezone,timedelta
import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import plotly.express as px
import io 
from st_aggrid import AgGrid


######## - FEATURE 1 - ########

st.title("Gantt chart of operating periods for the machine")

engine = create_engine('postgresql://lectura:ncorrea#2022@138.100.82.178:5432/2207')
df = pd.read_sql_query("SELECT id_var, date, value FROM variable_log_float WHERE id_var = 575 LIMIT 800", con=engine)

# Convert the values in the "date" column to datetime objects
df["date"] = pd.to_datetime(df["date"], unit="ms")


# Shift the "value" column by one row and store it in a new column called "prev_value"
# Use the fill_value parameter to specify a default value to use for the shifted rows
df["prev_value"] = df["value"].shift(fill_value=df["value"].iloc[0])

# Create an empty list to store the data for the Gantt chart
data = []

# Select the rows where the "value" changes from 255 to 0 or vice versa
rows = df.where((df["value"] == 0) & (df["prev_value"] == 255) | (df["value"] == 255) & (df["prev_value"] == 0))

#Iterate through the selected rows and create the data for the Gantt chart
for index, row in rows.iterrows():
    status = "on" if row["value"] == 255 else "off"
    start = row["date"]
    finish = df["date"].shift(-1).iloc[index]
    data.append({"status": status, "start": start, "finish": finish})


# Create the Gantt chart using the data
fig = px.timeline(data, x_start="start", x_end="finish", y="status")
fig.update_layout(title="Operational status (On/off)  during chosen timeframe Jan 31 2022 00:00 - Feb 1 2022 12:00")

#Show the Gantt chart

st.plotly_chart(fig)


######## - FEATURE 2 & 3 - ########

#We have 39 variables and some of them are TEMPERATURE_MOTOR...
b=pd.read_sql_query("select * from variable where name like '%%TEMPERATURE_MOTOR%%'", con=engine)
data_motor=pd.DataFrame(b)
id_var_motor=data_motor[['id','name']]
#We obtain a DataFrame with the list of variable of the motor, temperature. Now we are going to sort the variable
#So they can go from temperature_motor_x to temperature_motor_10
id_var_motor=id_var_motor.sort_values('id')
id_var_motor=id_var_motor.reset_index(drop=True)
#It is not perfect but at list the X,Y,Z motor are in first. We reindex in order to have the x value at rank 0
tab = pd.DataFrame(columns=["Name","Start","End","Duration"])


prog_names = pd.read_sql_query("select id_var, date, to_timestamp(@date/1000) as dateH, value from variable_log_string where id_var=594", con=engine)
prog_run = pd.read_sql_query("select id_var, date, to_timestamp(@date/1000) as dateH, value from variable_log_float where id_var = 575", con=engine) 


st.title("Evolution of the temperature of the motors through time")

# Choice of the time window
start_date = st.date_input("Start date",date(2022,1,30),date(2020,12,28),date(2022,2,23))
start_time = st.time_input("Start time",time(20,00,00))
end_date = st.date_input("End date",date(2022,2,2),date(2020,12,28),date(2022,2,23))
end_time = st.time_input("End time",time(12,00,00))

start_datetime = datetime.combine(start_date,start_time,tzinfo=timezone(timedelta(seconds=3600)))
end_datetime = datetime.combine(end_date,end_time,tzinfo=timezone(timedelta(seconds=3600)))


for i in range(len(prog_names)):
    row = []
    if prog_names["dateh"][i] > start_datetime and prog_names["dateh"][i] < end_datetime:
        row.append(prog_names["value"][i]) #put names in a new row
        row.append(prog_names["dateh"][i])
        found = 0
        index = 0
        while found == 0 and index < len(prog_run):
            if prog_names["dateh"][i] < prog_run["dateh"][index] and prog_run["value"][index] == 0.0:
                found = 1
                row.append(prog_run["dateh"][index])
            index = index + 1
    if row != []:
        tab = tab.append({'Name':row[0],'Start':row[1],'End':row[2],'Duration':row[2]-row[1]},ignore_index=True)

tab = tab[tab['Name'].str.len()>0]

st.text("Programs names and duations in the time window")

grid_response = AgGrid(
        tab,
        editable=True, 
        height=300, 
        width='100%',
        )

#With this we have roughtly an overview of the programms runned during a day
#We are going to sort tab in order to study the temperature evolution of the longest program
tab2=tab.sort_values('Duration',ascending=False)
tab2=tab2.reset_index(drop=True)
start_pg=tab2['Start'][0]
end_pg=tab2['End'][0]

#First we are only going to work with the temperature of the 3 axis motors
id_var_xyz=[]
for i in [0,1,2]:
    id_var_xyz.append(id_var_motor['id'][i])
temp_xyz=[]
#This is correct
for i in id_var_xyz:
    temp_xyz.append(pd.read_sql_query("select id_var, date, to_timestamp(@date/1000) as dateH, value from variable_log_float where id_var="+str(i)+" limit 10000", con=engine))

#Now we want to select only the temperature while the programm is running

for i in range(len(temp_xyz)):
    temp=temp_xyz[i]
    temp_xyz[i]=temp[(temp['dateh']>start_pg)&(temp['dateh']<end_pg)]

#We did reduced the number of value. Now we can plot if we want

st.text("Evolution of the temperature of the X axis motor during the time")
st.line_chart(temp_xyz[0])
st.text("Evolution of the temperature of the Y axis motor during the time")
st.line_chart(temp_xyz[1])
st.text("Evolution of the temperature of the Z axis motor during the time")
st.line_chart(temp_xyz[2])


######## - FEATURE 4 - ########

st.title("Gantt chart of Automatic/Manual mode")

pd.read_csv("C__Users_chlox_Documents_stream.csv")
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
        fig = px.timeline(
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



######## - FEATURE 5 - ########

st.title("Histogram per operating mode")

# Recuperation of all operating modes
OPmodes = pd.read_sql_query("select id_var, value from variable_log_float where id_var=622 limit 1000", con=engine)
list1=OPmodes["value"]
x= np.array(list1)
op_modes = np.unique(x).astype(str)[:-1]
def query(x):
    return pd.read_sql_query("".join(["select id_var, date, to_timestamp(@date/1000) as dateH, value from variable_log_float where id_var=622 and value=",x]),con=engine)
modes = [query(x) for x in op_modes]


# Choice of the time window
start_date = st.date_input("Start date",date(2020,12,28),date(2020,12,28),date(2022,2,23))
start_time = st.time_input("Start time",time(6,00,00))
end_date = st.date_input("End date",date(2020,12,28),date(2020,12,28),date(2022,2,23))
end_time = st.time_input("End time",time(22,00,00))

start_datetime = datetime.combine(start_date,start_time,tzinfo=timezone(timedelta(seconds=3600)))
end_datetime = datetime.combine(end_date,end_time,tzinfo=timezone(timedelta(seconds=3600)))

#Number of minutes in the interval
time_interval = end_datetime - start_datetime
time_interval_min = time_interval.seconds/60


# operations collected and operations per minute
counters_collected = []
counters_per_min = []


for mode in modes:
    op_collected = mode[mode['dateh'] > start_datetime][mode['dateh'] < end_datetime]['dateh'].size
    counters_collected.append(op_collected)
    counters_per_min.append(op_collected/time_interval_min)

st.text("Collected operations by operating mode")
st.bar_chart(counters_collected)

st.text("Collected operations per minute by operating mode")
st.bar_chart(counters_per_min)