import logging
import os
import argparse
from datetime import datetime, date, time, timedelta
from operator import itemgetter
from ConfigParser import ConfigParser
from github2.client import Github

logging.basicConfig(level=logging.ERROR)


def github_client():
    config = ConfigParser()
    config.read(os.path.join(os.getenv('HOME'), '.github'))
    per_sec = int(config.get('github', 'requests_per_second', 1))
    return Github(username=config.get('github', 'username'),
                  api_token=config.get('github', 'api_token'),
                  requests_per_second=per_sec)


class IssueTimeline(object):

    def __init__(self, github, repo_name):
        self.github = github
        self.repo_name = repo_name
        self.changes = []

    def load(self):
        changes = []
        for state in ('open', 'closed'):
            for issue in self.github.issues.list(self.repo_name, state=state):
                changes.append((issue.created_at, 1))
                if issue.closed_at:
                    changes.append((issue.closed_at, -1))
        changes.sort(key=itemgetter(0))
        self.changes = changes

    def issues_on(self, d):
        if not self.changes:
            self.load()
        d = datetime.combine(d, time())
        num = 0
        for change_date, change_diff in self.changes:
            if change_date < d:
                num += change_diff
            else:
                break
        return num

    def issues_by_date(self):
        if not self.changes:
            self.load()
        start_date = self.changes[0][0].date()
        end_date = self.changes[-1][0].date()
        num_days = int((end_date - start_date).total_seconds() / 86400)

        data = []
        for ii in range(num_days + 1):
            this = start_date + timedelta(days=ii)
            data.append((this.strftime('%m/%d/%Y'), self.issues_on(this)))

        tomorrow = end_date + timedelta(days=1)
        data.append(("NOW", self.issues_on(tomorrow)))
        return data


def horizontal_bar(data, plot_width=80, bar_char='#', values=True):
    label_width = max(len(row[0]) for row in data)
    data_range = max(row[1] for row in data)
    scale = (plot_width - label_width - 1) / data_range
    for label, value in data:
        label = label.rjust(label_width)
        bar_width = value * scale
        bars = bar_char * bar_width
        s = "%s %s" % (label, bars)
        if values:
            s += " %s" % value
        print s


def main():
    p = argparse.ArgumentParser(description='plots from github.')
    p.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                   help='print detailed output')
    p.add_argument('mode', type=str,
                   help='plot to generate',
                   choices=('issues',))
    p.add_argument('repos', metavar='repos', type=str, nargs='+',
                   help='repos to plot data for')
    args = p.parse_args()
    if args.verbose:
        print "Running %s for %s" % (args.mode, ', '.join(args.repos))

    github = github_client()
    if args.mode == 'issues':
        for repo in args.repos:
            print "Issue timeline for %s" % repo
            data = IssueTimeline(github, repo).issues_by_date()
            horizontal_bar(data)


if __name__ == '__main__':
    main()
