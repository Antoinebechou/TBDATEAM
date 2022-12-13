from datetime import datetime,date,time,timezone,timedelta
import streamlit as st
import pandas as pd
import numpy as np
import pytz
from matplotlib import pyplot as plt
from st_aggrid import AgGrid
from sqlalchemy import create_engine #to access a sql database


# pd.read_csv(r"G:\My Drive\Madrid\COURS\TBDA\TBDATEAM\data.csv")
# uploaded_file = st.file_uploader("Fill out the project plan template and upload your file here. After you upload the file, you can edit your project plan within the app.", type=['csv'])


engine = create_engine('postgresql://lectura:ncorrea#2022@138.100.82.178:5432/2207')

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
st.line_chart(temp_xyz[0],x='dateh',y='value')
st.text("Evolution of the temperature of the Y axis motor during the time")
st.line_chart(temp_xyz[1],x='dateh',y='value')
st.text("Evolution of the temperature of the Z axis motor during the time")
st.line_chart(temp_xyz[2],x='dateh',y='value')