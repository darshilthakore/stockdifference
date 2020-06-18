import requests
import json
import time
import sys
import logging

import redis
from rq import Queue
from worker import conn
from functions import apicalls

from flask import Flask, render_template, request, redirect, jsonify, url_for
app = Flask(__name__)


q = Queue(connection=conn)




app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.route("/")
def index():
    return render_template("home.html")

@app.route('/accept', methods=["POST","GET"])
def accept():
    timeList = {}
    headers = {'user-agent': 'Python script'}
    companyCode = request.form.get("companyCode")
    companyID = request.form.get("companyID")
    nseData = requests.get("https://www.nseindia.com/api/chart-databyindex?index=" + companyID + "EQN", headers=headers).json()

    bseData = requests.get("https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w?scripcode=" + str(companyCode) + "&flag=0&fromdate=&todate=&seriesid=").json()
    
    dataBSE = []

    

    for i in json.loads(bseData['Data']):
        timeList[str(i['dttm'])] = []
        dataBSE.append([str(i['dttm']), i['vale1']])
        timeList[str(i['dttm'])].append(i['vale1'])
        # print(i['dttm'])
    print(len(timeList))


    dataNSE = nseData['grapthData'] 

    newNse = []

    for j in dataNSE:
        # print(time.ctime(j[0] / 1000 - (5*60*60) - (30*60)))
        if time.strftime("%a %b %d %Y %H:%M:%S", time.localtime(j[0] / 1000 - (5*60*60) - (30*60))) in timeList:
            
            newNse.append([time.strftime("%a %b %d %Y %H:%M:%S", time.localtime(j[0] / 1000 - (5*60*60) - (30*60))), j[1]])
            timeList[time.strftime("%a %b %d %Y %H:%M:%S", time.localtime(j[0] / 1000 - (5*60*60) - (30*60)))].append(j[1])
        
    for i in list(timeList.keys()):
        if len(timeList[i]) != 2:
            del timeList[i]

    print(len(newNse))
    
    print(len(timeList))
    
    
    # print(nseData.json())
    # print(bseData.json())


    return render_template("index.html", datap=dataBSE, datan=newNse, timeList=timeList)

@app.route('/api/<companyCode>&<companyID>')
def api(companyCode,companyID):
    apidata = {}
    headers = {'user-agent': 'Python script'}
    companyCode = companyCode
    companyID = companyID
    # nseData = requests.get("https://www.nseindia.com/api/chart-databyindex?index=WIPROEQN", headers=headers).json()
    # print(nseData)
    # bseData = requests.get("https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w?scripcode=" + str(companyCode) + "&flag=0&fromdate=&todate=&seriesid=").json()
    url1 = "https://www.nseindia.com/api/chart-databyindex?index=WIPROEQN"
    url2 = "https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w?scripcode=" + str(companyCode) + "&flag=0&fromdate=&todate=&seriesid="
    
    job1 = q.enqueue(apicalls, url1)
    while not job1.result:
        time.sleep(2)
        # print(job1.result)
        nseData = job1.result
    job2 = q.enqueue(apicalls, url2)
    while not job2.result:
        time.sleep(2)
        # print(job2.result)
        bseData = job2.result


    for i in json.loads(bseData['Data']):
        apidata[str(i['dttm'])] = []
       
        apidata[str(i['dttm'])].append(i['vale1'])
    
    
    
    dataNSE = nseData['grapthData']
    
    for j in dataNSE:
        # print(time.ctime(j[0] / 1000 - (5*60*60) - (30*60)))
        if time.strftime("%a %b %d %Y %H:%M:%S", time.localtime(j[0] / 1000 - (5*60*60) - (30*60))) in apidata:
            
            apidata[time.strftime("%a %b %d %Y %H:%M:%S", time.localtime(j[0] / 1000 - (5*60*60) - (30*60)))].append(j[1])
        
    for i in list(apidata.keys()):
        if len(apidata[i]) != 2:
            del apidata[i]


    return jsonify(apidata)

if __name__ == "__main__":
    app.debug = True
    app.run()