#!/bin/python

import urllib, urllib2, base64, sys, json

if (len(sys.argv) != 4):
    print "This fetches ticket data related to a sprint.ly product and writes"
    print "it to sprintlyData.json"
    print ""
    print "Please run again with the following arguments:"
    print "1. Username"
    print "2. API key (from https://sprint.ly/account/profile/)"
    print "3. Sprintly product id"

    sys.exit();

username = sys.argv[1]
apiKey = sys.argv[2]
productId = sys.argv[3]

# Extract all data from sprintly for product
def request(path, data=None):
    if (data is None):
        request = urllib2.Request("https://sprint.ly/api" + path)
    else:
        request = urllib2.Request("https://sprint.ly/api" + path, data)
    base64string = base64.encodestring(
        '%s:%s' % (username, apiKey)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    result = urllib2.urlopen(request)
    return result.read()

products = request('/products.json')

items = []
limit = 30
highestItemNumber = -1

MAX_ITEM_LIMIT = 1000

def getItems(status, archived, offset=0):
    global limit, items, MAX_ITEM_LIMIT

    requestString = ('/products/' + str(productId) + '/items.json?limit=' + str(limit) + 
        '&status=' + status + '&offset=' + str(offset))
    
    if archived:
        requestString += "&archived=1"

    theseItems = json.loads(request(requestString))

    for item in theseItems:
        addItem(item)
        
        # get children if a story item
        if item['type'] == 'story':
            childItems = json.loads(
                request('/products/' + str(productId) + '/items/' + str(item['number']) + 
                    '/children.json'))

            print 'got ', len(childItems), ' child items'

            for childItem in childItems:
                addItem(childItem)
                
    print 'got ', len(theseItems), ' of status ', status
           
    if (len(theseItems) >= limit and offset < MAX_ITEM_LIMIT):
        getItems(status, archived, offset + limit)

def addItem(item):
    global highestItemNumber

    items.append(item)
    if item['number'] > highestItemNumber:
        highestItemNumber = item['number']

def getAllStatuses(archived):
    getItems("backlog", archived)
    getItems("in-progress", archived)
    getItems("completed", archived)
    getItems("accepted", archived)

getAllStatuses(False)
getAllStatuses(True)

print 'total items = ', len(items)

comments = {}

for number in range(1, highestItemNumber + 1):
    try:
        comment = json.loads(request('/products/' + str(productId) + '/items/' + str(number) + '/comments.json'))
        comments[number] = comment
        print 'got comments for item ', number
    except:   
        print "couldn't get comments for item ", number

output = {
    'items' : items,
    'comments' : comments
}

outFile = open('sprintlyData.json', 'w+')
outFile.write(json.dumps(output, indent=4))
outFile.close()
