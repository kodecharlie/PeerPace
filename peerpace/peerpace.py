# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import json
import requests
import sys
from datetime import date

###############################################################################
# Private functions.
###############################################################################

def calculate_performance_factors(last_week_sample, last_week_total, sorted_totals_array):
    num_weeks = len(sorted_totals_array)

    # Short-term factor for commits.
    factor_short_term = last_week_sample / last_week_total

    # Long-term factor for line deltas.
    if last_week_sample < sorted_totals_array[0]:
        # This could happen if the last week's sample is 0, and the sorted_totals_array
        # only incudes non-zero elements. This is equivalent to "worst" performance.
        factor_long_term = 0.0
    elif last_week_sample > sorted_totals_array[num_weeks-1]:
        # This should never happen, but if it does, assume "top" performance.
        factor_long_term = 1.0
    else:
        # If there are repeating elements in the array sorted_num_line_changes
        # starting at index sample_idx, then we underweight the contribution
        # here by referencing the earliest sample of the sequence of repeating 
        # elements. In effect, what we are calculating here is the cumulative
        # distribution function:  P(X <= x)
        sample_idx = sorted_totals_array.index(last_week_sample)
        factor_long_term = (sample_idx + 1.0) / num_weeks
    
    return [factor_short_term, factor_long_term]

###############################################################################
# Public functions.
###############################################################################

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
    print "Could not query stats for project " + project_name + " and git-user " + git_user_handle + ".\n"
    sys.exit(1)

stats = {
    'total_commits': 0,
    'total_line_changes': 0,
    'num_developers': 0,
    'weekly_counts': {}
}
last_week = {'num_commits': 0, 'num_line_changes': 0, 'timestamp': None}

cc_summary = json.loads(contributor_counts.text)
for developer in cc_summary:
    developer_author_login = developer['author']['login']
    stats['total_commits'] += developer['total']
    stats['num_developers'] += 1

    # Tally weekly stats. Weeks are ordered chronologically.
    for week in developer['weeks']:
        num_commits = week['c']
        num_line_changes = week['a'] + week['d']
        stats['total_line_changes'] += num_line_changes
        timestamp = week['w']
        if timestamp not in stats['weekly_counts']:
            stats['weekly_counts'][timestamp] = {'num_commits': 0, 'num_line_changes': 0}

        stats['weekly_counts'][timestamp]['num_commits'] += num_commits
        stats['weekly_counts'][timestamp]['num_line_changes'] += num_line_changes

        # Final week's samples will be written last.
        if developer_author_login == git_user_handle:
            last_week['num_commits'] = num_commits
            last_week['num_line_changes'] = num_line_changes
            last_week['timestamp'] = timestamp

# Calculate sorted arrays for both num_commits and num_line_changes.
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

# Default factors set to 0, meaning that when no work is done, implied performance is 0.
lines_short_term = 0
lines_long_term = 0
commits_short_term = 0
commits_long_term = 0
week_of = date.today().strftime("%A, %B %d, %Y")

# Calculate short- and long-term factors for line-deltas.
if last_week['timestamp'] != None and last_week['num_line_changes'] > 0 and last_week['num_commits'] > 0:
    [lines_short_term, lines_long_term] = calculate_performance_factors(
        last_week['num_line_changes'],
        stats['weekly_counts'][timestamp]['num_line_changes'],
        sorted_num_line_changes
    )
    [commits_short_term, commits_long_term] = calculate_performance_factors(
        last_week['num_commits'],
        stats['weekly_counts'][timestamp]['num_commits'],
        sorted_num_commits
    )
    week_of = date.fromtimestamp(last_week['timestamp']).strftime("%A, %B %d, %Y")

commits_factor = 0.5*commits_short_term + 0.5*commits_long_term
lines_factor = 0.5*lines_short_term + 0.5*lines_long_term
performance = 0.5*commits_factor + 0.5*lines_factor

print "During the week of " + week_of + ", performance for \"" + git_user_handle \
    + "\" on project \"" + project_name + "\" was {:.4f}.\n".format(performance)