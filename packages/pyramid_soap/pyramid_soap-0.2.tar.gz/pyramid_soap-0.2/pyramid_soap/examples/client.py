from suds.client import Client

url = 'http://127.0.0.1:8000/utsx?wsdl'
client = Client(url)
print client

result = client.service.GetStockPrice('Google', '2010-08-20T21:39:59')
print result

result = client.service.GetAverageStockPrice('Google', '2010-08-20T21:39:59')
print result

"""
url = 'http://jira.atlassian.com/rpc/soap/jirasoapservice-v2?wsdl'
client = Client(url)
print client

result = client.service.login('gmartinez', '231425')
print result
"""
