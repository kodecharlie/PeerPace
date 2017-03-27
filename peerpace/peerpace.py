# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import json
from pprint import pprint
import requests
import sys

project_name = "teamup"
git_user_handle = "kodecharlie"

# GET /repos/:owner/:repo/stats/contributors.
contributor_counts_endpt = 'https://api.github.com/repos/' + git_user_handle + '/' + project_name + '/stats/contributors'
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': 'Basic a29kZWNoYXJsaWU6OTE1YzdiMTg3NDY4OTY2MGRkM2UyNDI4NDE3NmY5NTA0NjkzOGJhMg=='
}
contributor_counts = requests.get(contributor_counts_endpt, headers=headers)

if contributor_counts.status_code != 200:
    sys.exit(1)

stats = {
    'total_commits': 0,
    'total_line_changes': 0,
    'num_developers': 0,
    'weekly_counts': {}
}
cc_summary = json.loads(contributor_counts.text)
for developer in cc_summary:
    print "Collecting stats for developer " + developer['author']['login'] + ":\n"
    stats['total_commits'] += developer['total']
    stats['num_developers'] += 1

    # Tally weekly stats. Weeks are ordered chronologically.
    for week in developer['weeks']:
        num_line_changes = week['a'] + week['d']
        stats['total_line_changes'] += num_line_changes
        timestamp = week['w']
        if timestamp not in stats['weekly_counts']:
            stats['weekly_counts'][timestamp] = {'num_commits': 0, 'num_line_changes': 0}

        stats['weekly_counts'][timestamp]['num_commits'] += week['c']
        stats['weekly_counts'][timestamp]['num_line_changes'] += num_line_changes

# Calculate empirical cumulative distribution functions for both num_commits and num_line_changes.
sorted_num_commits = []
sorted_num_line_changes = []
for timestamp in sorted(stats['weekly_counts']):
    # Ignore weeks during which there are neither commits nor line-changes.
    num_commits = stats['weekly_counts'][timestamp]['num_commits']
    num_line_changes = stats['weekly_counts'][timestamp]['num_line_changes']
    if num_commits <= 0 and num_line_changes <= 0:
        continue

    sorted_num_commits.append(stats['weekly_counts'][timestamp]['num_commits'])
    sorted_num_line_changes.append(stats['weekly_counts'][timestamp]['num_line_changes'])

sorted_num_commits.sort()
sorted_num_line_changes.sort()

print sorted_num_commits
print "\n\n"
print sorted_num_line_changes
# pprint(stats)

###############################################################################
# Stats for line deltas.
###############################################################################

# Get short-term stats.

# Get long-term stats.

###############################################################################
# Stats for commits.
###############################################################################

# Get short-term stats.

# Get long-term stats.

