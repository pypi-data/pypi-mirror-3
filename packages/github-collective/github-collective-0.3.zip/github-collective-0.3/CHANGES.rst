Changelog
=========

0.3 (2012-07-17)
----------------

 - Implement Buildout-style variable substitution for configuration with
   doctesting. 
   [davidjb]
 - Output resolved configuration when running in verbose mode.
   [davidjb]
 - Implement deletion of repos from configuration now GitHub API v3 
   supports this. *Warning*: if a repo exists on GitHub but not in 
   your configuration, it will now be deleted. Run the command in
   `pretend` mode first if unsure.
   [davidjb]
 - Optimise deletion process to not clear cache when attempting to 
   delete.
   [davidjb]
 - Add extras_require option for testing to use ``nose``.
   [davidjb]
 - Updating to depend on ``requests==0.13.1``.
   [davidjb] 


0.2 (2012-06-22)
----------------

 - Allow service hooks to be specified within the configuration.
   For samples, see the example configuration. Any GitHub supported
   hook can be associated with repos.
   [davidjb]
 - Allowing repo properties to be set on creation and editing of config.
   For available options, see http://developer.github.com/v3/repos/#create.
   This facilities private repo creation (if quota available), amongst other
   options.
   [davidjb]
 - Fix response parsing issue when creating teams.
   [davidjb]
 - Improved end-user documentation.
   [davidjb]

0.1.4 - 2012-02-19
------------------

 - adding support for requests==0.10.2 and removing pdb
   [`f561d79`_, garbas]

0.1.3 - 2011-07-09
------------------

 - fix caching file bug, cache now working
   [garbas]

0.1.2 - 2011-07-03
------------------

 - remane team to old_team to keep convention in sync.run method, using
   add instead of update on sets
   [`e48de49`_, garbas]
 - pretend should work for all except get reuqest type
   [`e098f9d`_, garbas]
 - nicer dump of json in cache file, unindent section which searches for
   repos defined in teams
   [`b8cb123`_, garbas]
 - we should write to cache file when there is no cache file avaliable
   [`fd7f9ee`_, garbas]

0.1.1 - 2011-07-02
------------------

 - and we have first bugfix relese, after refractoring and merging
   ``enable-cache`` branch.
   [`a09d174`_, garbas]


0.1 - 2011-07-02
----------------

 - initial release
   [garbas]

.. _`f561d79`: https://github.com/garbas/github-collective/commit/f561d79
.. _`e48de49`: https://github.com/garbas/github-collective/commit/e48de49
.. _`e098f9d`: https://github.com/garbas/github-collective/commit/e098f9d
.. _`b8cb123`: https://github.com/garbas/github-collective/commit/b8cb123
.. _`fd7f9ee`: https://github.com/garbas/github-collective/commit/fd7f9ee
.. _`a09d174`: https://github.com/garbas/github-collective/commit/a09d174
