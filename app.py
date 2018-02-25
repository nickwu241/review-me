import os
from itertools import chain
from dateutil.parser import parse
from pytz import UTC
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from github import Github

import boto3
import requests

GH_TOKEN = os.environ['REVIEWME_GH_TOKEN']
SLACK_INCOMING_WEBHOOK_URL = os.environ['REVIEWME_SLACK_URL']
DEFAULT_GH_REPO = 'nickwu241/review-me'
g = Github(GH_TOKEN)

app = Flask(__name__)
CORS(app)

s = None

class Status(object):
    READY = '- [x] READY FOR REVIEW'
    NOT_READY = '- [ ] READY FOR REVIEW'

    def __init__(self, repo_id, pr_number):
        self.repo_id = repo_id
        self.pr_number = pr_number
        self.pr = g.get_repo(self.repo_id).get_pull(self.pr_number)

    @property
    def comment(self):
        return self.pr.get_issue_comments()[0]

    @property
    def url(self):
        return self.pr.html_url

    @property
    def user(self):
        return self.pr.user.login

    @property
    def is_ready(self):
        # First line is READY or NOT_READY
        return self.READY in self.comment.body.split('\n')[0]

    @property
    def reviewers(self):
        # First line is READY or NOT_READY
        return [rline.lstrip('- ') for rline in self.comment.body.split('\n')[1:]]

    def uncheck(self):
        message = self.NOT_READY
        if self.reviewers:
            message += '\n- ' + '\n- '.join(self.reviewers)
        self.comment.edit(message)

    def add_reviewers(self, reviewers):
        for r in reviewers:
            self.comment.edit('{}\n- {}'.format(self.comment.body, r))

    def create_status(self):
        self.pr.create_issue_comment(self.NOT_READY)

    def should_notify(self):
        if not self.is_ready:
            return False

        resp = requests.get('https://api.github.com/repos/{}/pulls/{}/reviews'.format(
            DEFAULT_GH_REPO, self.pr_number
        ))
        if resp.status_code != requests.codes.ok:
            abort(500, "failed to access github reviews API")

        last_updated = self.comment.updated_at.replace(tzinfo=UTC)
        reviews_needed = {r: 0 for r in self.reviewers}
        approved_by = set()

        for review in resp.json():
            username = review['user']['login']
            if username not in self.reviewers:
                continue

            submitted_at = parse(review['submitted_at']).replace(tzinfo=UTC)
            print(submitted_at, last_updated)
            state_is_pending = review['state'] == 'PENDING'
            state_is_approved = review['state'] == 'APPROVED'
            asked_after_review = last_updated > submitted_at
            print('state:', review['state'])
            print('asked_after_review:', asked_after_review)
            if state_is_approved:
                approved_by.add(username)
                continue

            if state_is_pending or asked_after_review:
                reviews_needed[username] = max(reviews_need[username], last_updated - submitted_at)

        for comment in chain(self.pr.get_issue_comments(), self.pr.get_review_comments()):
            username = comment.user.login
            if username in approved_by or username not in self.reviewers:
                continue

            submitted_at = comment.updated_at.replace(tzinfo=UTC)
            print(submitted_at, last_updated)
            asked_after_review = last_updated > submitted_at
            print('asked_after_review:', asked_after_review)
            if asked_after_review:
                reviews_needed[username] = max(reviews_needed[username], last_updated - submitted_at)

        print(reviews_needed)
        print(approved_by)

        for a in approved_by:
            if a in reviews_needed:
                reviews_needed.pop(a)

        print(reviews_needed)

        return len(reviews_needed) > 0


class Notifier(object):
    SNS_main = boto3.resource('sns').Topic('arn:aws:sns:us-west-2:499885130140:review-me')
    SNS_unread = boto3.resource('sns').Topic('arn:aws:sns:us-west-2:499885130140:review-me-unread-notification')
    SLACK_INCOMING_WEBHOOK_URL = SLACK_INCOMING_WEBHOOK_URL

    @staticmethod
    def notify(status):
        message = 'PR by {} is ready for review at {}'.format(
            status.user,
            status.url
        )

        Notifier.sns(message)
        Notifier.slack(message)

        print('notify ' + ', '.join(status.reviewers))
        print(message)

    @staticmethod
    def slack(message):
        requests.post(Notifier.SLACK_INCOMING_WEBHOOK_URL, json={'text': message})

    @staticmethod
    def sns(message):
        Notifier.SNS_main.publish(Subject='Ready for review', Message=message)

    @staticmethod
    def sns_unread(message):
        Notifier.SNS_unread.publish(Subject='New Unread Github Notifications', Message=message)

@app.route('/')
def root():
    return 'Welcome to Nick\'s awesome app :)'

@app.route('/events', methods=['POST'])
def events():
    if 'X-GitHub-Event' not in request.headers:
        abort(401)

    if request.headers['X-GitHub-Event'] == 'issue_comment':
        handle_issue_comment(request.get_json())
    elif request.headers['X-GitHub-Event'] == 'pull_request':
        handle_pr(request.get_json())
    elif request.headers['X-GitHub-Event'] == 'pull_request_review':
        handle_pr_review(request.get_json())

    return 'OK'

@app.route('/notifications', methods=['GET'])
def notifications():
    notifications = g.get_user().get_notifications()
    messages = ['<{}|{}> ({}) at {}'.format(
                    n.subject.url, n.subject.title, n.subject.type, n.updated_at
                ) for n in notifications]

    if len(messages) == 0:
        return jsonify(notifications=False)
    msg = '{:d} unread GH Notifcations:\n{}'.format(len(messages), '\n'.join(messages))
    Notifier.slack(msg)
    Notifier.sns_unread(msg)

    return jsonify(notifications=True)

@app.route('/should_notify', methods=['GET'])
def should_notify():
    global s
    if not s:
        # Get default
        for issue in g.get_repo(DEFAULT_GH_REPO).get_issues():
            if issue.pull_request:
                s = Status(DEFAULT_GH_REPO, issue.number)
                print('using default status', DEFAULT_GH_REPO, issue.number)

    n = s.should_notify()
    print('should_notify:', n)
    if n:
        Notifier.notify(s)

    return(jsonify(n))

@app.route('/issues', methods=['GET'])
def issues():
    repos = request.args.get('repos').split(',')
    if not repos:
        abort(400)

    all_issues = []
    for repo in repos:
        for issue in g.get_repo(repo).get_issues():
            if issue.pull_request:
                # We don't want pull requests
                continue

            all_issues.append({
                'repo_name': issue.repository.name,
                'repo_url': issue.repository.html_url,
                'title': issue.title,
                'url': issue.html_url,
                'number': issue.number,
                'state': issue.state,
                'username': issue.user.login,
                'created_at': issue.created_at,
                'labels': [{'name': l.name, 'color': l.color} for l in issue.labels]
            })

    return jsonify(sorted(all_issues, key=lambda i: i['created_at'], reverse=True))

def handle_issue_comment(payload):
    global s
    repo_id = payload['repository']['id']
    pr_number = int(payload['issue']['pull_request']['url'].split('/')[-1])
    s = Status(repo_id, pr_number)
    if payload['action'] == 'edited':
        # A comment was edited
        # TODO: Make sure we only do work on the status comment getting edited
        if '[x]' in payload['comment']['body']:
            print('Ready for review')
        else:
            print('Not ready for review')
    elif payload['action'] == 'created' and pr_user(payload) != sender_user(payload):
        # Someone commented, uncheck ready for review
        s.uncheck()

def handle_pr(payload):
    global s
    if payload['action'] == 'opened':
        # Someone opened a PR
        s = Status(repo_id(payload), pr_number(payload))
        s.create_status()
    elif payload['action'] == 'review_requested':
        # Someone requested a PR
        s = Status(repo_id(payload), pr_number(payload))
        s.add_reviewers([r['login'] for r in payload['pull_request']['requested_reviewers']])

def handle_pr_review(payload):
    global s
    # Someone reviewed
    if payload['action'] == 'submitted':
        pass

    s = Status(repo_id(payload), pr_number(payload))
    s.uncheck()

def repo_id(payload):
    return payload['pull_request']['head']['repo']['id']

def pr_number(payload):
    return payload['pull_request']['number']

def pr_user(payload):
    return payload['issue']['user']['login']

def sender_user(payload):
    return payload['sender']['login']

def comment_timestamp(payload):
    return payload['comment']['updated_at']
