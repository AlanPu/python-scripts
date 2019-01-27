#!/usr/bin/env python
#coding=utf-8

import json
import urllib.request
import sys

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

global _accessKeyId
global _accessSecret
global _acsClient
global _RR
global _subDomain

def sendRequest(request):
	request.set_accept_format('json')
	request.set_domain('alidns.aliyuncs.com')
	request.set_method('POST')
	request.set_version('2015-01-09')

	return _acsClient.do_action(request)

def getSubDomainRecords():
	request = CommonRequest()
	request.set_action_name('DescribeSubDomainRecords')
	request.add_query_param('SubDomain', _subDomain)
	response = sendRequest(request)
	return json.loads(str(response, encoding = 'utf-8'))

def getCurrentIp():
	resp = urllib.request.urlopen('http://members.3322.org/dyndns/getip')
	resp = str(resp.read())
	return resp[2 : len(resp) - 3]

def updateDomainRecord(recordId, newIp):
	request = CommonRequest()
	request.set_action_name('UpdateDomainRecord')

	request.add_query_param('RecordId', recordId)
	request.add_query_param('RR', _RR)
	request.add_query_param('Type', 'A')
	request.add_query_param('SubDomain', _subDomain)
	request.add_query_param('Value', newIp)

	response = sendRequest(request)
	return json.loads(str(response, encoding = 'utf-8'))

def main():
	newIp = getCurrentIp()
	domainRecords = getSubDomainRecords()
	if domainRecords['TotalCount'] > 0:
		print("Found " + str(domainRecords['TotalCount']) + ' record')
		for rec in domainRecords['DomainRecords']['Record']:
			if rec['Value'] == newIp:
				print("IP no change, ignored")
			else:
				recordId = rec['RecordId']
				print('Updating ' + recordId + ' with new IP ' + newIp)
				response = updateDomainRecord(recordId, newIp)		
				print(response)
	else:
		print("No record found")

'''
Main function
argv[0] - File name, i.e. aliyun_ddns.py
argv[1] - Access key id
argv[2] - Access key secret
argv[3] - SubDomain, e.g. example.com
argv[4] - Host record, e.g. "@"" or "www", default value is "@", which is to resolve @.example.com
'''
if __name__ == '__main__':
	_accessKeyId = sys.argv[1]
	_accessSecret = sys.argv[2]
	_acsClient = AcsClient(_accessKeyId, _accessSecret, 'default')
	_RR = '@'
	if len(sys.argv) == 5:
		_RR = sys.argv[4]
	_subDomain = _RR + '.' + sys.argv[3]
	main()