from datetime import datetime
import time
import yaml
import requests
import os
import sys
# Add the parent directory to the sys.path to find the util module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.github_util import *

timestamp = int(datetime.now().timestamp())

# Load configuration from a YAML file
with open('../config.yaml', 'r') as file:
    config = yaml.safe_load(file)

def send_message(id, title, content, url):
    params = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh-CN": {
                    "title": title,
                    "content": [
                        [
                            {
                                "tag": "a",
                                "text": "#{}".format(id),
                                "href": url,
                            },
                            {
                                "tag": "text",
                                "text": content,
                            },
                        ]
                    ]
                }
            }
        }
    }

    resp = requests.post(config['webbook_url_gh_bot'], json=params)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") and result.get("code") != 0:
        print(f"发送失败：{result['msg']}")
        return
    print("消息发送成功")

def check_new_issues(repo_url, last_posted_issue_id):
    issues = make_github_request(repo_url, config['github']['token'])
    if last_posted_issue_id is None:
        last_posted_issue_id = int(issues[0]['number'])
        return last_posted_issue_id

    for issue in issues:
        id = issue['number']
        if int(id) > last_posted_issue_id:
            title = issue['title']
            url = issue['html_url']
            content = issue['body']
            send_message(id, title, content, url)

    return int(issues[0]['number'])

if __name__ == '__main__':
    last_posted_issue_id_1 = None
    last_posted_issue_id_2 = None
    repo_urls = [
        "https://api.github.com/repos/01-ai/Yi/issues",
        "https://api.github.com/repos/01-ai/Yi-1.5/issues"
    ]

    while True:
        print("Checking github new issues...")
        last_posted_issue_id_1 = check_new_issues(repo_urls[0], last_posted_issue_id_1)
        last_posted_issue_id_2 = check_new_issues(repo_urls[1], last_posted_issue_id_2)
        time.sleep(180)
