.. contents::

Introduction
============

collective.zestreleaser.aftercheckoutaction allows to execute any
shell action after a clean tag checkout has been done. The command
is executed in the context of hte checkout directory.
Some variables in the command string can be substituted:

 - name
   The package name
 - version
   The package version of the checkout

Commands can be written into ~/.pypirc, the section name must be
collective.zestreleaser.aftercheckoutaction.
The variable name is used to match the action against a package.
For each variable, this plugin compares the package name against
the variable name. If the variable name matches the beginning
of the package name, the action is executed. If multiple variable
name match, the longest variable name wins.

cza is a bit similar to gocept.zestreleaser.customupload.
While gza lets you upload the finished egg to a predefined location,
cza lets you do something with the clean checkout. Cza is intended to
be used if company policy demands that each released version of company
code must be committed to a company versioning system, but where the
actual development happens somewhere else. You should NOT use this
plugin to change something in the checkout, this would result in an
egg release that has different contents than what is in the source
repository

Example
=======
Add this to your local `~/.pypirc`::

    [collective.zestreleaser.aftercheckoutaction]
    collective.zestreleaser.aftercheckoutaction=svn import svn+ssh://do3cc@svn.zope.org/repos/main/Sandbox/do3cc/%(name)s/tags/%(version)s -m "Automatic commit"

This would execute an action for the package collective.zestreleaser.aftercheckoutaction.

