#!/usr/bin/env python
# encoding: utf-8
"""
backuprunner.py

Created by Manabu Terada on 2012-01-08.
Copyright (c) 2012 CMScom. All rights reserved.
"""
from StringIO import StringIO
from datetime import datetime
from functools import partial
import os
import json
import urllib2
from urllib2 import HTTPError
import base64
import xlwt
from mercurial import hg, ui, commands

BITBUCKET_API = u"https://api.bitbucket.org/1.0/"
BITBUCKET_BASE_URL = u"https://%(user)s:%(passwd)s@bitbucket.org/"
ISSUES_LOCATION = "issues"
ISSUE_HEADERS = [u'local_id', u'title', u'status', u'priority', u'content', u'created_on',
                 u'utc_last_updated',
                 ]
#ISSUE_HEADERS_DICT = [u'metadata', u'reported_by', u'responsible']
#ISSUE_COMMENT = [u'comment']

def _get_json_from_api(user, passwd, api_url):
    authString = base64.encodestring('%s:%s' % (user, passwd))
    headers = {'Authorization':"Basic %s" % authString}
    req = urllib2.Request(api_url, None, headers)
    try:
        bitbucket_obj = urllib2.urlopen(req)
    except HTTPError:
        raise Exception, "Could not get JSON from bitbucket"
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

def _get_issue_comment(comments):
    for data in comments:
        title = data.get('content')
        if title is None:
            title = u""
#        author = u"\n".join((u":".join(k, v) for k, v in data.get('author_info', {}).items() if v))
        author_dic = data.get('author_info', {})
        f_name = author_dic.get('first_name')
        l_name = author_dic.get('last_name')
        if f_name is not None and l_name is not None:
            author = f_name + u" " + l_name
        else:
            author = u""
        #author = author_dic.get('first_name') + u" " + author_dic.get('first_name')
        utc_updated_on = data.get('utc_updated_on')
        if utc_updated_on is None:
            utc_updated_on = u""
        yield u"\n".join((title, author, utc_updated_on))
        yield u"----------------"

def _save_excel_data(issues_folder_location, repo_name, issues, access_api_base, api_url):
    wb = xlwt.Workbook(encoding='utf-8')
    sheet1 = wb.add_sheet('issues')
    headers = ISSUE_HEADERS + [u'reported_by', u'responsible', u'comment']
    meta_headers = [u'kind', u'version', u'component', u'milestone']
    for i, head in enumerate(headers):
        sheet1.write(0, i, head)
    for ii, head in enumerate(meta_headers):
        sheet1.write(0, len(headers)+ii, head)

    for i, issue in enumerate(issues):
        raw = i + 1
        for ii, head in enumerate(headers):
            if head in ISSUE_HEADERS:
                sheet1.write(raw, ii, issue.get(head))
            elif head in [u'reported_by', u'responsible']:
                reported_dic = issue.get(head, {})
                f_name = reported_dic.get('first_name')
                l_name = reported_dic.get('last_name')
                if f_name is not None and l_name is not None:
                    sheet1.write(raw, ii, f_name + u" " + l_name)
                #data = reported_dic.get('first_name') + u" " + reported_dic.get('first_name')
                #sheet1.write(raw, ii, data)
            elif head == u'comment':
                if issue.get('comment_count') > 0:
                    comment_api_url = api_url + "/" + str(issue.get('local_id')) + "/comments"
                    comment_obj = access_api_base(comment_api_url)
                    comments = json.load(comment_obj)
                    data = _get_issue_comment(comments)
                    sheet1.write(raw, ii, "\n".join(data))
        metadata_dic = issue.get(u'metadata')
        for jj, head in enumerate(meta_headers):
            data = metadata_dic.get(head, '')
            if data:
                sheet1.write(raw, len(headers)+jj, data)

    date_str = datetime.now().strftime('%Y%m%d')
    with open(os.path.join(issues_folder_location, repo_name + date_str + ".xls"), 'wb') as f:
        wb.save(f)

def backup_isseus(access_api_base, repo_name, user, issues_folder_location):
    api_url = BITBUCKET_API + "repositories/" + user + "/" + repo_name.lower() + "/issues"
    bitbucket_obj = access_api_base(api_url+"?limit=50")
    issues_obj = json.load(bitbucket_obj)
    count = issues_obj.get('count', 0)
    issues = issues_obj.get('issues', [])
    for c in range(count / 50):
        start = str((c + 1) * 50)
        bitbucket_add_obj = access_api_base(api_url+"?limit=50&start="+start)
        issues_add = json.load(bitbucket_add_obj).get('issues', [])
        issues.append(issues_add)
    _save_excel_data(issues_folder_location, repo_name, issues, access_api_base, api_url)



def remove_old_issue_data(issues_folder_location, isseu_backup_count):
    def _cmp_mtime(x, y):
        x_file = os.path.join(issues_folder_location, x)
        y_file = os.path.join(issues_folder_location, y)
        return cmp(os.stat(x_file).st_mtime, os.stat(y_file).st_mtime)
    files = os.listdir(issues_folder_location)
    for i, path in enumerate(sorted(files,
        cmp=_cmp_mtime, reverse=True)):
        if i > isseu_backup_count:
            os.remove(os.path.join(issues_folder_location, path))

def backup_main(username, password, location, ignore_project, isseu_backup_count):
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
            remove_old_issue_data(issues_folder_location, isseu_backup_count)

if __name__ == '__main__':
    backup_main()

