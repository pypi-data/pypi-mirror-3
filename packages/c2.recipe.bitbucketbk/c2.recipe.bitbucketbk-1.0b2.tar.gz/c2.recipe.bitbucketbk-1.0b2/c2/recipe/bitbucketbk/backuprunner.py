#!/usr/bin/env python
# encoding: utf-8
"""
backuprunner.py

Created by Manabu Terada on 2012-01-08.
Copyright (c) 2012 CMScom. All rights reserved.
"""
from functools import partial
import os
import json
import urllib2
import base64
import xlwt
from mercurial import hg, ui, commands

BITBUCKET_API = u"https://api.bitbucket.org/1.0/"
BITBUCKET_BASE_URL = u"https://%(user)s:%(passwd)s@bitbucket.org/"
ISSUES_LOCATION = "issues"
ISSUE_HEADERS = [u'local_id', u'title', u'status', u'priority', u'content', u'created_on',
                 u'utc_last_updated',
                 ]
ISSUE_HEADERS_DICT = [u'metadata', u'reported_by', u'responsible']
ISSUE_COMMENT = [u'comment']

def _get_json_from_api(user, passwd, api_url):
    authString = base64.encodestring('%s:%s' % (user, passwd))
    headers = {'Authorization':"Basic %s" % authString}
    req = urllib2.Request(api_url, None, headers)
    bitbucket_obj = urllib2.urlopen(req)
    return bitbucket_obj

def get_repositories(access_api_base, user):
    """Longin & get repositories"""
    api_url = BITBUCKET_API + "users/" + user
    bitbucket_obj = access_api_base(api_url)
    repos = json.load(bitbucket_obj).get('repositories', [])
    for repo in repos:
        yield repo.get('name', None), repo.get('scm', ''), repo.get('has_issues')

def has_repo(repo_name, location):
    if os.path.exists(os.path.join(location, repo_name)):
        return True
    else:
        return False

def create_hg_repo(repo_url, location):
    # repo = hg.repository(ui.ui(), repo_url)
    commands.clone(ui.ui(), repo_url, dest=location, insecure=True)

def get_hg_data(repo_url, location):
    repo = hg.repository(ui.ui(), location)
    commands.pull(ui.ui(), repo, source=repo_url)

def _get_issue_comment(schema):
    return ""

def _save_excel_data(issues_folder_location, repo_name, issues):
    wb = xlwt.Workbook(encoding='utf-8')
    sheet1 = wb.add_sheet('issues')
    headers = ISSUE_HEADERS + ISSUE_HEADERS_DICT + ISSUE_COMMENT
    for i, head in enumerate(headers):
        sheet1.write(0, i, head)
    for i, issue in enumerate(issues):
        raw = i + 1
        for j, head in enumerate(headers):
            if head in ISSUE_HEADERS:
                sheet1.write(raw, j, issue.get(head))
            elif head in ISSUE_HEADERS_DICT:
                data = u"\n".join((u":".join((k, v)) for k, v in issue.get(head, {}).items() if v))
                sheet1.write(raw, j, data)
            elif head in ISSUE_COMMENT:
                if issue.get('comment_count') > 0:
                    data = _get_issue_comment(head)
                    sheet1.write(raw, j, data)
    with open(os.path.join(issues_folder_location, repo_name + ".xls"), 'wb') as f:
        wb.save(f)

def backup_isseus(access_api_base, repo_name, user, issues_folder_location):
    api_url = BITBUCKET_API + "repositories/" + user + "/" + repo_name + "/issues"
    bitbucket_obj = access_api_base(api_url)
    issues = json.load(bitbucket_obj).get('issues', [])
    _save_excel_data(issues_folder_location, repo_name, issues)


def backup_main(username, password, location, ignore_project):
    """Main method, gets called by generated bin/bitbucketbk.
    """
    if not os.path.exists(os.path.join(location, ISSUES_LOCATION)):
        os.mkdir(os.path.join(location, ISSUES_LOCATION))
    access_api_base = partial(_get_json_from_api, username, password)
    repos = get_repositories(access_api_base, username)
    for repo_name, scm, has_issues in repos:
        if repo_name in ignore_project:
            continue
        base_url = BITBUCKET_BASE_URL % {'user' : username, 'passwd' : password}
        repo_url = base_url + username + u'/' + repo_name.lower()
        if not isinstance(repo_url, str):
            repo_url = repo_url.encode('utf-8')
        folder_location = os.path.join(location, repo_name)
        if not isinstance(folder_location, str):
            folder_location = folder_location.encode('utf-8')

        if scm == u"hg":
            if not has_repo(repo_name, location):
                create_hg_repo(repo_url, folder_location)
            else:
                get_hg_data(repo_url, folder_location)

        if has_issues:
            issues_folder_location = os.path.join(location, ISSUES_LOCATION, repo_name)
            if not os.path.exists(issues_folder_location):
                os.mkdir(issues_folder_location)
                backup_isseus(access_api_base, repo_name, username, issues_folder_location)
            else:
                backup_isseus(access_api_base, repo_name, username, issues_folder_location)

if __name__ == '__main__':
    backup_main()

