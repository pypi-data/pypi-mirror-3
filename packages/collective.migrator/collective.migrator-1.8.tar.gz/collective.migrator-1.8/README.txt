Introduction
============


collective.migrator is a buildout based tool to help migrate content between Plone/Zope instances.
It can be installed as follows:

    ``$ easy_install collective.migrator``


Once installed you can run the tool to set up the migration environment

    ``$ migrator``


This creates a folder called *migrator* and installs a buildout environment there. All further actions are run from this folder.

The first thing that you want to do at this point is customize the *instance.cfg* file.

By default it looks like this::

    [remote]
    host = xxx.webfactional.com
    user = ssh_user
    port = 8080
    extensions = /usr/Plone-2.5.5/zeocluster/client1/Extensions
    zmi_user = admin
    zmi_pwd = admin
    root = Plone
    export = /usr/Plone-2.5.5/zeocluster/client1/var
    
    [local]
    host = localhost
    port = 8080
    extensions = /home/suresh/plone4/parts/instance/Extensions
    zmi_user = admin
    zmi_pwd = admin
    root = Plone
    import = /home/suresh/plone4/var/instance/import


This defines the settings for all the Plone instances involved in the migration.

The *buildout.cfg* defines the steps that will be executed as part of the migration.

Here is the default content::

    [buildout]
    extends = instance.cfg
        migrate_frontpage.cfg
        migrate_users.cfg
        migrate_props.cfg
    parts =
    tbd = 
        ${migrate_frontpage:parts}
        ${migrate_users:parts}
        ${migrate_props:parts}


As you can see, *parts* has been intentionally left blank. Also *instance.cfg* described previously is being used here. The other *migrate_*.cfg* files contain some sample steps to move various objects between the instances.

As a simple test, you can change *parts* in *buildout.cfg* to look like this::

    parts = export_frontpage


This step is defined in *migrate_frontpage.cfg*.

Now after you run buildout as follows:

``$ bin/buildout``


you should notice that the front-page object has been exported in the remote Plone instance. Once you gain more confidence in the tool, you can even try to run the other steps found in the *migrate_*.cfg* files.

PS: This may not be the "coolest" way to manipulate your Plone and some of these actions may be better done with GenericSetup profiles, but this worked for me!


Troubleshooting
===============

A couple of people have reported the following error::

    # migrator
    INFO: Starting migraton.
    Traceback (most recent call last):
      File "/opt/python/bin/migrator", line 5, in ?
        from pkg_resources import load_entry_point
    ImportError: No module named pkg_resources 

Not sure what causes this, but I suspect a flawed python installation. *virtualenv* is a good tool
to protect against this situation. The following modified installation procedure can be used in this
case::

    $ easy_install virtualenv
    $ virtualenv --no-site-packages <my-folder>
    $ . <my-folder>/bin/activate
    $ easy_install -U setuptools
    $ easy_install -U zc.buildout
    $ easy_install collective.migrator
    $ migrator  
