Basic authentication plugin, suitable for customization
to work towards other authentication backends.

Gives users who authenticate the roles Editor, Reviewer
and Member.  To change the roles given, edit config.py

Just customize authenticate in plugin.py if you want
to authenticate towards a different kind of backend,
say POP, PAM, MySQL or anything you like, really.  :)

Thanks to PAS, PluggableAuth authors and Jeremy Stark, who wrote:

http://plone.org/documentation/kb/simple-plonepas-example/tutorial-all-pages

-Morten (morten@nidelven-it.no)
