====================
Buildout from GitHub
====================

GitHub has become a commonly-used SCM tool for software engineering teams.
The purpose of this Buildout extension is to enable the retrieval of source
tarballs and static downloads from private repositories by using the API v3's
token-based authentication, combined with a bit of URL rewriting to retrieve
files using the API server instead of the main website when required.

Please see the sections below for setup usage instructions.


Set Up: Request an API Key
==========================

Before you can access private repositories from this module, you must create
and store an API key on each system running buildout. Unlike the v2 API where
one key was issued per user, you may create as many keys as you like and
revoke them at will.

API keys are tied to an individual user account.

You can create API v3 key using ``curl`` (please substitute your own GitHub
user name):

    curl -s -X POST -d '{}' -u ${user} https://api.github.com/authorizations \
        | grep token

If you plan to make multiple keys for distribution to different systems (e.g.
automated build environment), you might want to include a description to be
able to distinguish them from one another later:

    curl -s -X POST -d '{"note": "build001.mydomain.ext"}' -u ${user} \
        https://api.github.com/authorizations | grep token

Now configure the value of github.token to the hash returned from the command
above:

    git config --global github.token ${token}

For details on managing authorization GitHub's OAuth tokens, see the API
documentation: http://developer.github.com/v3/oauth/#oauth-authorizations-api


Usage: GitHub Repository Downloads
==================================

You can instruct Buildout to download a tarball of any refid from your
repository by specifying the same URL as you would use in your browser to
retrieve it, using the following syntax:

    https://github.com/${user}/${project}/${archivetype}/${refid}

**Important Note:** The url *must* use the ``https`` protocol to be retrieved
using this extension; URLs using the ``http`` protocol will be ignored.

In practice, you would typically use this to retrieve a tarball for
installation as an egg in your buildout file, using a recipe similar to this:

    [buildout]
    find-links =
        https://github.com/me/myproject/tarball/master#egg=myproject

    eggs = myproject

    parts = myproject

    [myproject]
    unzip = true
    recipe = zc.recipe.egg
    path = myproject

These URLs will be rewritten on demand to retrieve the


Usage: GitHub Static Downloads
==============================

Static downloads that have been previously uploaded to your GitHub project
may also be retrieved using the same URL you would use in your browser,
formed as follows:

    https://github.com/downloads/${user}/${project}/${filename}

**Important Note:** As with repository downloads, the url *must* use the
``https`` protocol to be retrieved.

Since these files can contain static software releases as eggs or anything
else you want (media files, configuration data, etc.) it is up to you how
to use them in your buildout; a common pattern is to install them as a part
in a fashion similar to the following example:

    [buildout]
    parts = mypart

    [mypart]
    recipe = hexagonit.recipe.download
    url = https://github.com/downloads/me/myproject/myfile.tar.gz


Credits
=======

Thanks to Bernd Dorn, Jürgen Kartnaller, Bernd Rössl and the rest at Lovely
Systems for lovely.buildouthttp (upon which this project is based), and to
Clayton Parker and Tarek Ziade for bugfixes and extensions.

