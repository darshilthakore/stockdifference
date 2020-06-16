import requests
import json
import time

from flask import Flask, render_template, request, redirect, jsonify, url_for
app = Flask(__name__)

@app.route('/')
def index():

    headers = {'user-agent': 'Python script'}
    companyCode = 532540
    companyID = "TCS"
    nseData = requests.get("https://www.nseindia.com/api/chart-databyindex?index=TCSEQN", headers=headers)

    bseData = requests.get("https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w?scripcode=" + str(companyCode) + "&flag=0&fromdate=&todate=&seriesid=")
    

    timeList = []

    for i in json.loads(bseData.json()['Data']):
        timeList.append(str(i['dttm']))
        # print(i['dttm'])
    print(len(timeList))

    dataNSE = nseData.json()['grapthData'] 

    newNse = []

    for j in dataNSE:
        # print(time.ctime(j[0] / 1000 - (5*60*60) - (30*60)))
        if time.strftime("%a %b %d %Y %H:%M:%S", time.localtime(j[0] / 1000 - (5*60*60) - (30*60))) in timeList:
            print("inside if")
            newNse.append([time.strftime("%a %b %d %Y %H:%M:%S", time.localtime(j[0] / 1000 - (5*60*60) - (30*60))), j[1]])

    print(len(newNse))
    
    
    # print(nseData.json())
    # print(bseData.json())


    return render_template("index.html", datap=bseData.json(), datan=newNse)