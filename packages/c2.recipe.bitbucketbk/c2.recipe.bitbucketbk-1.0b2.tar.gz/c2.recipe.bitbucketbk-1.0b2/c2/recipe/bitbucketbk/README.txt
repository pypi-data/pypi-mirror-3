Supported options
=================

The recipe supports the following options:

username
    username of bitbucket.org

password
    password of bitbucket.org

location
    backup location
    default : buckups

ignore_project
	option
	Listing project name, if do you have no backup project 

Example usage
=============

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = bitbucketbk
    ...
    ... [bitbucketbk]
    ... recipe = c2.recipe.bitbucketbk
    ... username = %(username)s
    ... password = %(password)s
    ... location = %(location)s
    ... """ % { 'username' : 'value1', 'password' : 'value2', 'location' : 'value3'})

Running the buildout gives us::

    >>> print 'start', system(buildout) 
    start...
    Installing bitbucketbk.
    Unused options for bitbucketbk: 'location' 'password' 'username'.
    <BLANKLINE>


Backup
=============

Calling ``bin/bitbucketbk``

    >>> import sys
    >>> write('bin', 'bitbucketbk',
    ...       "#!%s\nimport sys\nprint ' '.join(sys.argv[1:])" % sys.executable)
    >>> dontcare = system('chmod u+x bin/bitbucketbk')

By default, backups are done in ``var/bitbucketbk``::

    >>> print system('bin/bitbucketbk')
    ...
