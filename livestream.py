# (*) To communicate with Plotly's server, sign in with credentials file
import plotly.plotly as py
import plotly.tools as tls
# (*) Graph objects to piece together plots
from plotly.graph_objs import *
import numpy as np  # (*) numpy for math functions and arrays
import datetime
import time

import serial
import requests
from relayr import Client
from relayr.api import Api

def serialmonitor():
    ser = serial.Serial('/dev/ttyACM0', 115200)
    while True:
       ch = ser.readline()
       if 'B' in  ch:
           print ch

def call_tropo():
   http_headers = {'Content-Type': 'application/json'}
   r = requests.get('http://10.206.18.74:8080/publish/call', headers=http_headers)
   print r.content

def send_data_to_plotly(): 
    tls.set_credentials_file(stream_ids=[
        "l2jcjzwcag",
        "vd0uk9bn68",
        "gb7zo82zbm",
        "h9zzpurc0q"
    ])
    a = Api(token='ENtcsvfM9tOT0.ktctGbJDdAyxZtKVEF')
    stream_ids = tls.get_credentials_file()['stream_ids']
    print (stream_ids)
    stream_id = stream_ids[0]
    stream_id2 = stream_ids[1]

    # Make instance of stream id object 

    stream = Stream(
     token=stream_id,  # (!) link stream id to 'token' key
     maxpoints=80      # (!) keep a max of 80 pts on screen
     )

    stream2 = Stream(
     token=stream_id2,  # (!) link stream id to 'token' key
     maxpoints=80      # (!) keep a max of 80 pts on screen
     )
     # Initialize trace of streaming plot by embedding the unique stream_id

    trace1 = Scatter(
     x=[],
     y=[],
     mode='lines+markers',
     stream=stream         # (!) embed stream id, 1 per trace

     )

    trace2 = Scatter(
     x=[],
     y=[],
     mode='lines+markers',
     stream=stream2         # (!) embed stream id, 1 per trace

     )
    data = Data([trace1])
    data2 = Data([trace2])

    # Add title to layout object
    layout = Layout(title='BPM Series')
    layout2 = Layout(title='Heartbeat monitoring')

    # Make a figure object
    fig = Figure(data=data, layout=layout)
    fig2 = Figure(data=data2, layout=layout2)

    # (@) Send fig to Plotly, initialize streaming plot, open new tab
    #unique_url = py.plot(fig, filename='s7_first-stream')
    # (@) Make instance of the Stream link object, 
    #     with same stream id as Stream id object

    s = py.Stream(stream_id)
    s2 = py.Stream(stream_id2)

    # (@) Open the stream
    s.open()
    s2.open()


    # Delay start of stream by 5 sec (time to switch tabs)
    time.sleep(5)
    ser = serial.Serial('/dev/ttyACM0', 115200)
    while True:
        ch = ser.readline()
        x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        if 'B' in  ch:
            print ch
            chfin = ch.split('B')
            print chfin[1]  

            # Current time on x-axis, random numbers on y-axis
            y = int(chfin[1])    

            # POST data to relayr
            #finstr = "\'" + chfin[1] + "\'"
            #print finstr
            finstr = chfin[1].rstrip()
            data = {'meaning' : 'bpm', 'value' : finstr }
            print data 
            a.post_device_data('7ccfb852-2203-4616-8cbf-cdf55471abc9', data)
            # (@) write to Plotly stream!
            s.write(dict(x=x, y=y))

            # (!) Write numbers to stream to append current data on plot,
            #     write lists to overwrite existing data on plot (more in 7.2).
        elif 'S' in ch:
            print ch
            chfinS = ch.split('S')
            print chfinS[1] 
            y1 = int(chfinS[1])
            s2.write(dict(x=x, y=y1)) 

        time.sleep(0.08)  # (!) plot a point every 80 ms, for smoother plotting

    # (@) Close the stream when done plotting

    s.close()
    s2.close()
send_data_to_plotly()
