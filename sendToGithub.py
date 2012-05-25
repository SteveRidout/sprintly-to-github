#!/bin/python

import urllib, urllib2, base64, sys, json
from datetime import datetime

if (len(sys.argv) != 5):
    print "This pushes sprintly data in sprintlyData.json to github"
    print ""
    print "Please run again with the following arguments:"
    print "1. Github username"
    print "2. Github password"
    print "3. Repo owner name (username or organization name)"
    print "4. Repo name"

    sys.exit();

username = sys.argv[1]
password = sys.argv[2]
ownerName = sys.argv[3]
repoName = sys.argv[4]

# Extract all data from sprintly for product
def request(path, method='GET', data=None):
    print 'path: ', path
    print 'data: ', data
    if (data is None):
        request = urllib2.Request("https://api.github.com" + path)
    else:
        request = urllib2.Request("https://api.github.com" + path, data)
    base64string = base64.encodestring(
        '%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    request.get_method = lambda: method
    result = urllib2.urlopen(request)
    return result.read()

def prettyDate(timestampString):
    # TODO: allow timezones other than +00:00
    return str(datetime.strptime(timestampString, '%Y-%m-%dT%H:%M:%S+00:00'))

data = json.loads(open('sprintlyData.json', 'r').read())

byStatus = { "backlog":[], "in-progress":[], "completed":[], "accepted":[] }
byNumber = {}

for item in data['items']:
    byNumber[item['number']] = item
    byStatus[item['status']].append(item)

for key in byStatus:
    print key, ': ', len(byStatus[key])

highestNumber = 0

for key in byNumber:
    if key > highestNumber:
        highestNumber = key
    print key, ': ', byNumber[key]['title']

print 'highestNumber = ', highestNumber

# get current issues
openIssues = json.loads(request('/repos/' + ownerName + '/' + repoName + '/issues'))
closedIssues = json.loads(request('/repos/' + ownerName + '/' + repoName + '/issues?state=closed'))

currentIssues = openIssues + closedIssues

highestGithubIssue = 0

for issue in currentIssues:
    if issue['number'] > highestGithubIssue:
        highestGithubIssue = issue['number']

print 'higheset github issue = ', highestGithubIssue

if highestGithubIssue > 0:
    print 'WARNING: some issues already exist in this repo'

# create black issues if neccessary
for number in range(highestGithubIssue + 1, highestNumber + 1):
    print 'create blank issue ', number
    request('/repos/' + ownerName + '/' + repoName + '/issues', 'POST',
        json.dumps({
            'title': 'Blank issue - Sprintly importer',
            'state': 'closed'
        }))

labels = []
for label in json.loads(request('/repos/' + ownerName + '/' + repoName + '/labels')):
    labels.append(label['name'])

# amend to reflet data from sprintly
for item in data['items']:
    creator = item['created_by']['first_name'] + ' ' + item['created_by']['last_name']

    body = 'Imported from Sprint.ly\n'
    body += '\nOriginal Creator: ' + creator
    body += '\nCreated at: ' + prettyDate(item['created_at'])
    body += '\n\n'
    body += item['description']
    
    state = 'open'
    if (item['status'] == 'completed'):
        state = 'closed'

    issue = {
        'title': item['title'],
        'body': body,
        'state': state
    }

    if 'tags' in item:
        issue['labels'] = item['tags']

        # create labels if needed
        for tag in item['tags']:
            if not (tag in labels):
                request('/repos/' + ownerName + '/' + repoName + '/labels', 'POST',
                    json.dumps({
                        'name' : tag,
                        'color' : 'FF2222'
                        }))
                labels.append(tag)

    print 'amended issue: ', item['number'], ': ', json.dumps(issue, indent=4)
    
    request('/repos/' + ownerName + '/' + repoName + '/issues/' + str(item['number']),
        'POST', json.dumps(issue))

# add comments
for number in data['comments']:
    comments = data['comments'][number]
    
    currentComments = json.loads(
        request('/repos/' + ownerName + '/' + repoName + '/issues/' + number + '/comments'))

    # delete existing comments
    for comment in currentComments:
        request('/repos/' + ownerName + '/' + repoName + '/issues/comments/' +
                str(comment['id']), method="DELETE")

    for comment in comments:
        creator = comment['created_by']['first_name'] + ' ' + comment['created_by']['last_name']

        body = 'Imported from Sprint.ly\n'
        body += '\nOriginal Creator: ' + creator
        body += '\nCreated at: ' + prettyDate(comment['created_at'])
        body += '\n\n'
        body += comment['body']

        print 'add comment: ', body
        request('/repos/' + ownerName + '/' + repoName + '/issues/' + number + '/comments',
            'POST',
            json.dumps({
                'body': body
            }))

