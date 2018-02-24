import os

from flask import Flask, request, abort, jsonify
from github import Github
import boto3
import requests

GH_TOKEN = os.environ['REVIEWME_GH_TOKEN']
SLACK_INCOMING_WEBHOOK_URL = os.environ['REVIEWME_SLACK_URL']
g = Github(GH_TOKEN)

app = Flask(__name__)

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
        return READY in self.comment

    @property
    def reviewers(self):
        # First line is READY or NOT_READY
        return [rline.lstrip('- ') for rline in self.comment.body.split('\n')[1:]]

    def uncheck(self):
        self.comment.edit(self.NOT_READY + '\n' + '\n'.join(self.reviewers))

    def add_reviewers(self, reviewers):
        for r in reviewers:
            self.comment.edit('{}\n- {}'.format(self.comment.body, r))

    def create_status(self):
        self.pr.create_issue_comment(self.NOT_READY)

    def should_notify(self):
        if not self.is_ready:
            return False

        # TODO: Check if should_notify
        # self.pr.get_issue_comments()
        # self.pr.get_review_comments()
        # self.comment.last_updated


class Notifier(object):
    SNS = boto3.resource('sns').Topic('arn:aws:sns:us-west-2:499885130140:review-me')
    SLACK_INCOMING_WEBHOOK_URL = SLACK_INCOMING_WEBHOOK_URL

    @staticmethod
    def notify(status):
        message = 'PR by {} is ready for review at {}'.format(
            status.user,
            status.url
        )

        # Notifier.sns(message)
        # Notifier.slack(message)

        print('notify ' + ', '.join(status.reviewers))
        print(message)

    @staticmethod
    def slack(message):
        requests.post(Notifier.SLACK_INCOMING_WEBHOOK_URL, json={'text': message})

    @staticmethod
    def sns(message):
        Notifier.SNS.publish(Subject='Ready for review', Message=message)

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
    Notifier.slack('{:d} unread GH Notifcations:\n{}'.format(len(messages), '\n'.join(messages)))
    return jsonify(notifications=len(messages) != 0)

def handle_issue_comment(payload):
    repo_id = payload['repository']['id']
    pr_number = int(payload['issue']['pull_request']['url'].split('/')[-1])
    s = Status(repo_id, pr_number)
    if payload['action'] == 'edited':
        # A comment was edited
        # TODO: Make sure we only do work on the status comment getting edited
        if '[x]' in payload['comment']['body']:
            print('Ready for review')
            Notifier.notify(s)
        else:
            print('Not ready for review')
    elif payload['action'] == 'created' and pr_user(payload) != sender_user(payload):
        # Someone commented, uncheck ready for review
        s.uncheck()

def handle_pr(payload):
    if payload['action'] == 'opened':
        # Someone opened a PR
        s = Status(repo_id(payload), pr_number(payload))
        s.create_status()
    elif payload['action'] == 'review_requested':
        # Someone requested a PR
        s = Status(repo_id(payload), pr_number(payload))
        s.add_reviewers([r['login'] for r in payload['pull_request']['requested_reviewers']])

def handle_pr_review(payload):
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
