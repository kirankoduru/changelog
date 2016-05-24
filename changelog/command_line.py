import re
import sys
import argparse
from datetime import datetime
from subprocess import Popen, PIPE

def parse_logs(logs, fields):
    logs = logs.strip('\n\x1e').split("\x1e")
    logs = [row.strip().split("\x1f") for row in logs]
    logs = [dict(zip(fields.keys(), row)) for row in logs]
    return logs

def print_logs(new_version, logs, issue_id_pattern):
    date_today = datetime.now().strftime('%d %b %Y')
    print '###{0} ({1})'.format(new_version, date_today)
    for item in logs:
        title = item['subject']
        issues = re.findall(issue_id_pattern, title + item['body'])
        if issues:
            for issue in issues:
                if ('Merge branch' in title) or ('Merge pull' in title):
                    continue
                print '- {0} ([{1}](http://company.com/browse/{1}))'.format(title, issue)

        else:
            if ('Merge branch' in title) or ('Merge pull' in title):
                continue
            print '- {0}'.format(title)

def run_command(from_, to, new_version, issue_id_pattern):
    # fields to fetch from commit log
    # For format parameters refer: https://git-scm.com/docs/pretty-formats
    fields = {
        'id': '%H',
        'author_name': '%an',
        'author_email': '%ae',
        'date': '%ad',
        'subject': '%s',
        'body': '%b'
    }
    format_str = '%x1f'.join(fields.values()) + '%x1e'
    command = 'git log {0}...{1} --format="{2}"'.format(from_, to, format_str)
    p = Popen(command, shell=True, stdout=PIPE)
    (logs, _) = p.communicate()
    logs = parse_logs(logs, fields)
    print_logs(new_version, logs, issue_id_pattern)

def init_argparser():
    parser = argparse.ArgumentParser(
                description='Publish CHANGELOG from git commits'
    )
    parser.add_argument(
            '-s', '--start', 
            type=str, required=True,
            help='Enter commit/tag/branch you want CHANGELOG from'
    )
    parser.add_argument(
            '-e', '--end',
            type=str, 
            help='Enter commit/tag/branch you want CHANGELOG till. \
                  Default value is set to master'
    )
    parser.add_argument(
            '-v', '--version',
            type=str, required=True, 
            help='Enter new version number for the CHANGELOG'
    )
    parser.add_argument(
            '-i', '--issue',
            type=str,
            help='Enter issue ID pattern'
    )
    return parser.parse_args()

def main():
    args = init_argparser()
    from_ = args.start
    to_ = args.end
    new_version = args.version
    issue_id_pattern = args.issue

    # set defaults
    if not to_:
        to_ = 'master'

    if not issue_id_pattern:
        issue_id_pattern = r'#\d+'

    run_command(from_, to_, new_version, issue_id_pattern)

if __name__ == '__main__':
    sys.exit(main())
