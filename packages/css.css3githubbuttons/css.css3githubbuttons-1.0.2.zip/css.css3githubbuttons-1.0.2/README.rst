css.css3githubbuttons
*********************

Introduction
============

This library packages `CSS3 GitHub Buttons`_ for `fanstatic`_.

There's a lot of versions of this CSS library floating around,
so we're currently using the one provided by ``necolas`` on GitHub.
If development moves elsewhere, we can adjust the library accordingly.
If you're using this and notice a change in development at
https://github.com/necolas/css3-github-buttons/network (such as
someone has taken over development more than original author or is otherwise
doing more work) before we do, let us know or send a pull request.

Usage
=====

Install using your favourite method (``pip``, ``easy_install``, ``buildout``,
etc) and then in your code do this::

    import css.css3githubbuttons
    css.css3githubbuttons.buttons.need()

This requires integration between your web framework and ``fanstatic``,
and making sure that the original resources (shipped in the ``resources``
directory in ``css.css3githubbuttons``) are published to some URL.

For Pyramid, this can be as simple as installing and utilising 
`pyramid_fanstatic`_.

Updating this package
=====================

Given this package uses the latest (at the time of writing) GitHub master
of the CSS library, it may (will) need updating at some point.  Do this
at the base of the repository::

    pushd css/css3githubbuttons/resources/css3-github-buttons/
    wget https://raw.github.com/necolas/css3-github-buttons/master/gh-icons.png
    wget https://raw.github.com/necolas/css3-github-buttons/master/gh-buttons.css
    popd
    git commit -a -m "Updating to latest version"
    git push

Note
----

We could use Git submodules but setuptools seems to *hate* them,
``setuptools-git`` really doesn't want to agree with them,
``zest.releaser`` doesn't support recursive cloning (yet; pull request
sent), and so forth. Feel free to help improve this situation! Yikes!

So, let's resort to manually copying the files out of GitHub.

.. _`fanstatic`: http://fanstatic.org
.. _`CSS3 GitHub Buttons`: https://github.com/necolas/css3-github-buttons
.. _`pyramid_fanstatic`: http://pypi.python.org/pypi/pyramid_fanstatic


