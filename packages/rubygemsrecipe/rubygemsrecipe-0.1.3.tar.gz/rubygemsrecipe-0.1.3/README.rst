*******************************
Recipe for installing ruby gems
*******************************

Using this recipe you can easily install ruby gems packages into buildout
environment.

All executable files from gem packages are available in ``bin-directory``.

Usage
=====

::

    [buildout]
    parts =
        rubygems

    [rubygems]
    recipe = rubygemsrecipe
    gems =
        sass

After running buildout you can use SASS from buildout environment::

    ./bin/sass --version

Options
=======

gems
    list of gem package names.

version
    rubygems version, if not specified, recipe will try to find most recent
    version.
