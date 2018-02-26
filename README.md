# Review Me
Have you ever

- had to wait forever for your Pull Requests (PRs) to get reviewed because your reviewers forgot about your PR?
- forgot to review someone else's PRs?
- struggled with keeping track of issues across multiple tightly related repositories?
- wished you could get Github notifications through other services such as Slack rather than only Emails?

If you answered yes to any of those questions, Review Me aims to solve all of those struggles!

Review Me offers automatic notifications to remind PR reviewers, multi-repo issue list, and slack notifications for un-read Github notifications for better productivity.

Built using: React, Flask, AWS (EC2, SNS, SQS, SMS, SES, S3, DynamoDB), Github API, Github Webhooks, Slack API, Javascript, Python, and <3

## Demo
Dashboard:
<img src="https://raw.githubusercontent.com/nickwu241/review-me/master/demo/dashboard1.png" />
<img src="https://raw.githubusercontent.com/nickwu241/review-me/master/demo/dashboard2.png" />

One place to see ALL issues across multiple repositories:
<img src="https://raw.githubusercontent.com/nickwu241/review-me/master/demo/issues.png" />

Automatic scheduled Slack, Email, SMS notifications to remind reviewers about unreviewed PRs:
<img src="https://raw.githubusercontent.com/nickwu241/review-me/master/demo/ask_reviewer_email.png" />
<img src="https://raw.githubusercontent.com/nickwu241/review-me/master/demo/ask_reviewer_email.png" />
<img src="https://raw.githubusercontent.com/nickwu241/review-me/master/demo/ask_reviewer_sms.png" width="auto" height="640px"/>

Slack notifications for your Github notifications:
<img src="https://raw.githubusercontent.com/nickwu241/review-me/master/demo/unread_notifications_slack.png" />
