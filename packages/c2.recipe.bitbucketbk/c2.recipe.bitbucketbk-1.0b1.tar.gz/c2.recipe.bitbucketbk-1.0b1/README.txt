Requirement
================

This recipe supports Python 2.6+, because using 'json' module.


Information
================

- Code repository: https://bitbucket.org/cmscom/c2.recipe.bitbucketbk
- Questions and comments to terada@cmscom.jp
- Report bugs at https://bitbucket.org/cmscom/c2.recipe.bitbucketbk/issues


Simple usage
==============

Modify buildout.cfg ::

    parts = 
       ...
       bitbucketbk

    [bitbucketbk]
    recipe = c2.recipe.bitbucketbk
    username = xxxxxxxxxxxxx
    password = xxxxxxxxxxxxxxxxxx
    location = /backups
    ignore_project =
        xxxxxx1
        xxxxxx2

Run the buildout ::

    bin/buildout -N

You can use backup scripts ::

    bin/bitbucketbk

You will see backups in  `/backups`.



Cron job integration
===========================

For example ::

	[backupcronjob]
	recipe = z3c.recipe.usercrontab
	times = 0 12 * * *
	command = ${buildout:directory}/bin/bitbucketbk


