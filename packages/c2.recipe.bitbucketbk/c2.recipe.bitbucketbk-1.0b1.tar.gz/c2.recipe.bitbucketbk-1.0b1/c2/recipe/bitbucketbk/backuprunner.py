#!/usr/bin/env python
# encoding: utf-8
"""
backuprunner.py

Created by Manabu Terada on 2012-01-08.
Copyright (c) 2012 CMScom. All rights reserved.
"""

import sys
import os
import json

import urllib2
import base64

from mercurial import hg, ui, commands

BITBUCKET_API = u"https://api.bitbucket.org/1.0/"
BITBUCKET_BASE_URL = u"https://%(user)s:%(passwd)s@bitbucket.org/"

def get_repositories(user, passwd):
    """Longin & get repositories"""
    api_url = BITBUCKET_API + "users/" + user

    authString = base64.encodestring('%s:%s' % (user, passwd))
    headers = {'Authorization':"Basic %s" % authString}
    req = urllib2.Request(api_url, None, headers)
    bitbucket_obj = urllib2.urlopen(req)

    repos = json.load(bitbucket_obj).get('repositories', [])
    for repo in repos:
        yield repo.get('name', None), repo.get('scm', ''), repo.get('main_branch', u'null')

def has_repo(repo_name, location):
    if repo_name in os.listdir(location):
        return True
    else:
        return False

def create_hg_repo(repo_url, location):
    # repo = hg.repository(ui.ui(), repo_url)
    commands.clone(ui.ui(), repo_url, dest=location, insecure=True) 
    

def get_hg_data(repo_url, location):
    repo = hg.repository(ui.ui(), location)
    commands.pull(ui.ui(), repo, source=repo_url) 
    

def backup_main(username, password, location, ignore_project):
    """Main method, gets called by generated bin/bitbucketbk.
    """
    repos = get_repositories(username, password)
    for repo_name, scm, main_branch in repos:
        if repo_name in ignore_project:
            continue
        if main_branch == u'null':
            continue
        if scm == u"hg":
            base_url = BITBUCKET_BASE_URL % {'user' : username, 'passwd' : password}
            repo_url = base_url + username + u'/' + repo_name.lower()
            if not isinstance(repo_url, str):
                repo_url = repo_url.encode('utf-8')
            folder_location = os.path.join(location, repo_name)
            if not isinstance(folder_location, str):
                folder_location = folder_location.encode('utf-8')
            if not has_repo(repo_name, location):
                create_hg_repo(repo_url, folder_location)
            else:
                get_hg_data(repo_url, folder_location)
        else:
            return None

if __name__ == '__main__':
    backup_main()

