# -------------------------------------------------------------
# GEOvis4.0 REST API
# Example for access GEOvis4.0
# Created: 26.01.2022 / M. Fehr
# Python 3.8.12
# -------------------------------------------------------------
import sys
from datetime import datetime, timedelta
import requests
import json
import numpy as np
import pandas as pd


def login(login_data):
    url = 'https://geovis.io/api/rest/login'
    response = requests.post(url, json=login_data)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    # print(data)
    #print('-------------------------------------------------------------')
    auth_token = data['Data']
    header = {'Authorization': 'Bearer ' + auth_token}
    return header



def getAllRelatedProjects(header):
    url = 'https://geovis.io/api/rest/projects'
    response = requests.get(url, headers=header)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    print(data)
    print('-------------------------------------------------------------')
    return data

def getProjectInfo(header, projectID):
    url = 'https://geovis.io/api/rest/project/' + str(projectID)
    response = requests.get(url, headers=header)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    print(data)
    print('-------------------------------------------------------------')

def getSensorsNames(header, projectID, filter):
    url = 'https://geovis.io/api/rest/sensors/' + str(projectID)
    response = requests.post(url, json=filter, headers=header)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    #print(data)
    #print('-------------------------------------------------------------')
    return data

def getSensorsData(header, projectID, filter):
    url = 'https://geovis.io/api/rest/sensorsData/' + str(projectID)
    response = requests.post(url, json=filter, headers=header)
    response.encoding = 'utf-8-sig'
    return json.loads(response.text)
    #print(data)
    #print('-------------------------------------------------------------')


def getSensorsProperties(header, projectID, filter):
    url = 'https://geovis.io/api/rest/sensorsProperties/' + str(projectID)
    response = requests.post(url, json=filter, headers=header)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    print(data)
    print('-------------------------------------------------------------')


def SyncSensors(header, projectID, filter):
    url = 'https://geovis.io/api/rest/sync/' + str(projectID)
    response = requests.post(url, json=filter, headers=header)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    print(data)
    print('-------------------------------------------------------------')


def getProjectViews(header, projectID):
    url = 'https://geovis.io/api/rest/views/' + str(projectID)
    response = requests.get(url, headers=header)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    print(data)
    print('-------------------------------------------------------------')


def getViewInfo(header, projectID, viewID):
    url = 'https://geovis.io/api/rest/view/' + str(projectID) + "/" + str(viewID)
    response = requests.get(url, headers=header)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    print(data)
    print('-------------------------------------------------------------')


def addSensorsToView(header, projectID, viewID, sensors):
    url = 'https://geovis.io/api/rest/addSensorsToView/' + str(projectID) + "/" + str(viewID)
    response = requests.post(url, json=sensors, headers=header)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    print(data)
    print('-------------------------------------------------------------')


def removeSensorsFromView(header, projectID, viewID, sensors):
    url = 'https://geovis.io/api/rest/removeSensorsFromView/' + str(projectID) + "/" + str(viewID)
    response = requests.post(url, json=sensors, headers=header)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    print(data)
    print('-------------------------------------------------------------')   


def changeDataStates(header, projectID, sensors):
    url = 'https://geovis.io/api/rest/changeStates/' + str(projectID)
    response = requests.post(url, json=sensors, headers=header)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    print(data)
    print('-------------------------------------------------------------')


def deleteSensorData(header, projectID, sensors):
    url = 'https://geovis.io/api/rest/delete/' + str(projectID)
    response = requests.post(url, json=sensors, headers=header)
    response.encoding = 'utf-8-sig'
    data = json.loads(response.text)
    print(data)
    print('-------------------------------------------------------------')
