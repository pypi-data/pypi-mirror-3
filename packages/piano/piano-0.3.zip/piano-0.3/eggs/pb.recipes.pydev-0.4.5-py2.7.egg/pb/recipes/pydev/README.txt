pb.recipes.pydev
================

.. contents::

Author: Tiberiu Ichim, tibi@pixelblaster.ro

Overview
********

This recipe is about modifying a `.pydevproject` file, which is used by Eclipse
and PyDev to hold a list of folders which hold Python packages (for code
completition, auto-import and so on). This recipe won't generate a new one! 
If you're running the buildout directly in the PyDev project, you're all set,
otherwise you have to set the path to the .pydevproject file.

The idea is to fill this file with paths pointing to the used egg folders. 
Although this recipe is written with a zope3 instance in mind, it can probably 
be used for any other scenario (read integration.txt for details on how to use 
with Plone). After running the buildout you'll have to close and reopen the 
Eclipse project (refreshing the source code might also work), to regenerate 
the project's module indexes.

How it works
************

    >>> import os

A full recipe would include the following options:

    >>> write(sample_buildout, 'buildout.cfg',
    ... """
    ... [buildout]
    ... parts = pydev
    ...
    ... [pydev]
    ... recipe = pb.recipes.pydev
    ... pydevproject_path = ${buildout:directory}/.pydevproject_test
    ... extra-paths = /something/else
    ... remote_path = /media/my_share/my_project
    ... eggs = pb.recipes.pydev
    ... """)

We need a working .pydevproject file. This recipe won't generate a new one.
I'll use this project's project file for testing.

    >>> fc = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    ... <?eclipse-pydev version="1.0"?>
    ... <pydev_project>
    ... <pydev_pathproperty name="org.python.pydev.PROJECT_SOURCE_PATH">
    ... <path>/pb.recipes.pydev/src</path>
    ... </pydev_pathproperty>
    ... <pydev_property name="org.python.pydev.PYTHON_PROJECT_VERSION">python 2.4</pydev_property>
    ... <pydev_pathproperty name="org.python.pydev.PROJECT_EXTERNAL_SOURCE_PATH">
    ... <path>/home/tibi/workspace3.3/pb.recipes.pydev/eggs/zc.buildout-1.0.0b31-py2.4.egg</path>
    ... <path>/home/tibi/workspace3.3/pb.recipes.pydev/eggs/zc.recipe.egg-1.0.0-py2.4.egg</path>
    ... </pydev_pathproperty>
    ... </pydev_project>"""
    >>> pf_path = os.path.join(sample_buildout, '.pydevproject_test')
    >>> f = open(pf_path, 'w')
    >>> f.write(fc)
    >>> f.close()

Now we can run the buildout

    >>> print system(buildout) #doctest: +NORMALIZE_WHITESPACE
    Installing pydev.

With this recipe we only override the external source paths entry, so we'll only
check that:

    >>> import os
    >>> from xml.dom import minidom
    >>> document = minidom.parse(os.path.join(sample_buildout,
    ...                             '.pydevproject_test'))
    >>> nodes = document.getElementsByTagName('pydev_pathproperty')
    >>> paths_node = filter(lambda node: (node.getAttribute('name') ==
    ...                     'org.python.pydev.PROJECT_EXTERNAL_SOURCE_PATH'),
    ...                nodes
    ...             )[0]
    >>> data = paths_node.toxml()

The paths should contain what we have specified int eh the `extra-paths` option:

    >>> '/something/else' in data
    True

In our sample buildout.cfg we have placed, in the `eggs` option, this recipe's
egg. In your projects, this can be anything, (and it should be your developing
application's egg name, as declared in your `setup.py`). The `pb.recipes.pydev`
egg depends on `zc.recipe.egg`, `zc.buildout` and `setuptools`, let's see if
all these were included.

    >>> 'zc.recipe.egg' in data
    True
    >>> 'zc.buildout' in data
    True
    >>> 'setuptools' in data
    True

Note: at this moment, the project's source path is also included, in theory it
shouldn't affect Eclipse.

    >>> code_path = __file__[:len(__file__) -
    ...                          len('/src/pb/recipes/pydev/README.txt')]
    >>> pydev_egg_src = os.path.join(code_path, 'src')
    >>> pydev_egg_src in data
    True

Eggs are sub-folders of remote_path, so Eclipse will be able to find them threw network shares.
    >>> '/media/my_share/my_project' in data
    True

In version 0.2 the paths were added twice, let's check that this doesn't happen
anymore:

    >>> data.count('zc.recipe.egg')
    1

In version 0.3, the recipe would fail with a .pydevproject file with no external
source path node, let's check this doesn't happen anymore:

    >>> fc = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    ... <?eclipse-pydev version="1.0"?>
    ... <pydev_project>
    ... <pydev_pathproperty name="org.python.pydev.PROJECT_SOURCE_PATH">
    ... <path>/pb.recipes.pydev/src</path>
    ... </pydev_pathproperty>
    ... </pydev_project>"""
    >>> pf_path = os.path.join(sample_buildout, '.pydevproject_test')
    >>> f = open(pf_path, 'w')
    >>> f.write(fc)
    >>> f.close()
    >>> print system(buildout) #doctest: +NORMALIZE_WHITESPACE
    Updating pydev.
    >>> import os
    >>> from xml.dom import minidom
    >>> document = minidom.parse(os.path.join(sample_buildout,
    ...                             '.pydevproject_test'))
    >>> nodes = document.getElementsByTagName('pydev_pathproperty')
    >>> paths_node = filter(lambda node: (node.getAttribute('name') ==
    ...                     'org.python.pydev.PROJECT_EXTERNAL_SOURCE_PATH'),
    ...                nodes
    ...             )[0]
    >>> data = paths_node.toxml()
    >>> '/something/else' in data
    True
    >>> 'zc.recipe.egg' in data
    True
    >>> 'zc.buildout' in data
    True
    >>> 'setuptools' in data
    True
