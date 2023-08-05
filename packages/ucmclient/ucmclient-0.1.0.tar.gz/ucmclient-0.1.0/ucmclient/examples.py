__author__ = 'stuart robinson'

from ucmclient import UcmClient, ServiceFailed

#connect to ucm with specified hostname and content server port

ucmClient = UcmClient('ucmserver.example.com','16200')
ucmClient.login('weblogic','password')


#build a dictionary of service parameters.
ucmServiceData ={
    'dDocTitle':'New Article 1',
    'dDocName':'News_Article_01',
    'dDocType':'News',
    'dDocAuthor':'weblogic',
    'dDocAccount':'weblogic',
    'dSecurityGroup':'Public',
    #files can be submitted using an open file object
    'primaryFile':open('news.txt','r')
}

try:
    ucmClient.call_service('CHECKIN_UNIVERSAL',ucmServiceData)
except ServiceFailed as e:
    print 'checkin failed - %s' % e


#Search for files of type News
ucmServiceData = {
        'QueryText':'dDocType<matches>`News`',
        'ResultCount':10
}

try:
    search = ucmClient.call_service('GET_SEARCH_RESULTS',ucmServiceData)
    #Access resultset by name and iterate through results
    for doc in search.fetch('SearchResults'):
        print doc['dDocName']

except ServiceFailed as e:
    print 'search failed - %s' % e

