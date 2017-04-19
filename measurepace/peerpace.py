import base64
import json
import requests
import sys
from datetime import date
from statistics import mean, variance

class PeerPace:
    ###############################################################################
    # "Private" functions.
    ###############################################################################

    def calculate_performance_factors(
        self,
        last_week_sample,
        last_week_total,
        developer_stats,
        github_username
    ):
        # Short-term factor.
        factor_short_term = (float(last_week_sample) / last_week_total) if (last_week_total > 0) else 0

        # Long-term factor.
        git_developer_ltm = -1
        steadiness = {}
        for developer in developer_stats:
            if developer_stats[developer]['var'] <= 0:
                cur_steadiness = float(inf)
            else:
                cur_steadiness = float(developer_stats[developer]['mu']) / developer_stats[developer]['var']

            steadiness[developer] = cur_steadiness
            if github_username == developer:
                git_developer_ltm = steadiness[developer]

        ltm_values = steadiness.values()
        if git_developer_ltm <= 0 or len(ltm_values) <= 0:
            factor_long_term = 0
        else:
            ltm_values.sort()
            git_developer_ltm_index = ltm_values.index(git_developer_ltm)
            factor_long_term = (1.0 + git_developer_ltm_index) / len(ltm_values)

        return [factor_short_term, factor_long_term]

    ###############################################################################
    # Everything else.
    ###############################################################################

    #
    # Goto Account Settings. Under "Developer settings", visit "Personal access tokens".
    # Here, you can create a custom oauth token for accessing your private repos.
    #
    # Return 0 on completion without error; return number less than 0 on error.
    #
    def calculate_programmer_performance(
        self,
        github_username,
        github_project_name,
        personal_access_token,
        impact_of_code_commits,
        impact_of_line_changes,    # unused for now.
        impact_of_past_behavior
    ):
        # Use HTTP Basic authentication to acess github API.
        authorization = base64.b64encode(github_username + ":" + personal_access_token)

        # GET /repos/:owner/:repo/stats/contributors.
        contributor_counts_endpt = 'https://api.github.com/repos/' + github_username + '/' + github_project_name + '/stats/contributors'
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'Basic ' + authorization
        }
        contributor_counts = requests.get(contributor_counts_endpt, headers=headers)

        if contributor_counts.status_code != 200:
            error_msg = "Could not query stats for project " + github_project_name + " and git-user " + github_username
            return json.dumps({'status': -1, 'error': error_msg})

        stats = {
            'total_commits': 0,
            'total_line_changes': 0,
            'num_developers': 0,
            'weekly_totals': {},
            'developer_stats': {},
        }
        last_week = {'num_commits': 0, 'num_line_changes': 0, 'timestamp': None}

        cc_summary = json.loads(contributor_counts.text)
        for developer in cc_summary:
            developer_author_login = developer['author']['login']
            stats['total_commits'] += developer['total']
            stats['num_developers'] += 1

            if not stats['developer_stats'].keys():
                stats['developer_stats']['code_commits'] = {}
                stats['developer_stats']['line_changes'] = {}

            code_commits = []
            line_changes = []

            # Tally weekly stats. Weeks are ordered chronologically.
            for week in developer['weeks']:
                num_commits = week['c']
                num_line_changes = week['a'] + week['d']
                stats['total_line_changes'] += num_line_changes
                timestamp = week['w']

                if timestamp not in stats['weekly_totals']:
                    stats['weekly_totals'][timestamp] = {'num_commits': 0, 'num_line_changes': 0}

                stats['weekly_totals'][timestamp]['num_commits'] += num_commits
                stats['weekly_totals'][timestamp]['num_line_changes'] += num_line_changes
                
                if num_commits > 0 or num_line_changes > 0:
                    code_commits.append(num_commits)
                    line_changes.append(num_line_changes)

                # Final week's samples will be written last.
                if developer_author_login == github_username:
                    last_week['num_commits'] = num_commits
                    last_week['num_line_changes'] = num_line_changes
                    last_week['timestamp'] = timestamp

            # Calculate mean and variance.
            stats['developer_stats']['code_commits'] = {
                developer_author_login: {
                    'mu': mean(code_commits) if len(code_commits) > 0 else 0,
                    'var': variance(code_commits) if len(code_commits) > 1 else 0
                }
            }
            stats['developer_stats']['line_changes'] = {
                developer_author_login: {
                    'mu': mean(line_changes) if len(line_changes) > 0 else 0,
                    'var': variance(line_changes) if len(line_changes) > 1 else 0
                }
            }

        if last_week['timestamp'] != None:
            timestamp = last_week['timestamp']
            week_of = date.fromtimestamp(timestamp).strftime("%A, %B %d, %Y")

            # Calculate short- and long-term factors for line-deltas and code-commits.
            [lines_short_term, lines_long_term] = self.calculate_performance_factors(
                last_week['num_line_changes'],
                stats['weekly_totals'][timestamp]['num_line_changes'],
                stats['developer_stats']['line_changes'],
                github_username
            )
            [commits_short_term, commits_long_term] = self.calculate_performance_factors(
                last_week['num_commits'],
                stats['weekly_totals'][timestamp]['num_commits'],
                stats['developer_stats']['code_commits'],
                github_username
            )
        else:
            week_of = date.today().strftime("%A, %B %d, %Y")
            # Default factors set to 0, meaning that when there is no project history, implied performance is 0.
            lines_short_term = 0
            lines_long_term = 0
            commits_short_term = 0
            commits_long_term = 0

        commits_factor = (1.0-impact_of_past_behavior)*commits_short_term + impact_of_past_behavior*commits_long_term
        lines_factor = (1.0-impact_of_past_behavior)*lines_short_term + impact_of_past_behavior*lines_long_term
        performance = impact_of_code_commits*commits_factor + (1.0-impact_of_code_commits)*lines_factor

        # Done.
        return json.dumps({
            'status': 0,
            'week_of': week_of,
            'github_username': github_username,
            'github_project_name': github_project_name,
            'performance': performance
        })
