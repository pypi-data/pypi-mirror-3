=======
plywood
=======

::

    load('url')
    load('compress')
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width; initial-scale=1.0">
        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>

        compress('css'):
          <link rel='stylesheet' type='text/css' href=static('css/reset.css')>
          <link rel='stylesheet' type='text/css' href=static('css/welcome.css')>

        compress('js'):
          <script src=static("js/underscore.js") type="text/javascript"></script>
          <script src=static("js/backbone.js") type="text/javascript"></script>

        ieif 'lt IE 9':
          <script src="//html5shiv.googlecode.com/svn/trunk/html5.js" type="text/javascript"></script>
          <link rel='stylesheet' type='text/css' href=static('css/ie.css') />
        <title>
          # plain text is quoted
          'Welcome'
          # or escaped
          e(' to B&B')  # => ' to B&amp;B'
          if title:
            # docstrings are stripped of preceding whitespace (and so they *must* be
            # indented), and the first and last newline is removed.  In this
            # example, "| THE TITLE" will be printed, with no newline in front or back.
            """
            | {title} | {title!safe}
            """
            # string interpolation *pretty much* uses format, but the !h flag
            # indicates that auto-escaping should not occur.  Also, any python
            # expression that could occur in a lambda
        block('extra_head')  # blocks, and block inheritance?  of course!
      <body>
        <div.wrapper#wrapper (is_internal and '.internalClass')>
          <header>
            block('header'):
              <p class="logo">
              block('header_title'):
                if user:
                  'Welcome, '{user.name}'
                else:
                  'Welcome'
            if current_member:
              <p class="login">
                "Welcome, {current_member.preferred_name}"
                <a href=url("logout")> Log Out
          <nav>
            <ul>
              block('nav'):
                <li><a href=url("login")> Login

        <!--
          multiline HTML comments, like this
          one, are not included in the output.
        -->

          <section class="breadcrumb">
            block('breadcrumb')

          <section class="main">
            block('messages'):
              if messages:
                <ul class="messages">
                  for message in messages:
                    <li class=message.tags> {message}
            <script>
              $(document).ready(function(){
                $("ul.messages").addClass("animate");

                var fade_out = _(function() {
                  this.addClass("fade-out")
                }).bind($("ul.messages"))

                setTimeout(fade_out, 5000);
                $("ul.messages").bind("click", fade_out);
              });
            </script>  # this is optional!
            block('content')
          <footer>
            <p>
              This is a footer
              <span> | </span>
              &copy;2012 colinta


------------
INSTALLATION
------------

::

    $ pip install plywood
    $ ply < in.ply > out.html

------
SYNTAX
------

Each line starts with a statement, which can either be a function
(``div``, ``block``) a literal (``'literal'``, ``'''literal'''``), or a control
statement (``if truthy:``, ``else:``, ``for row in rows:``).

Functions get called with the arguments and a "block"::

    # arguments are ((), {}), block is Block()
    p
    # arguments are ((), {'class': 'divvy'}), block is Block()
    div(class="divvy")
    # arguments are (('autofocus'), {'id': 'bio'}), block is Block(Literal('This is my bio'),)
    textarea(autofocus, id="bio"): 'This is my bio'

Even if there is no "block", you'll get at the least at empty block object that
you can call ``block.render`` on.  It will be "falsey", though, so you can check
for the existence of a block.  The minimum "truthy" block is an empty string.
That means ``div ''`` will give you a "truthy" block, but ``div`` will be a
"falsey" block.

----------
EXTENSIONS
----------

You can extend the crap out of plywood, because ``div``, ``if``, ``block``, the
whole lot, are all written as plywood extensions.  Without the builtin
extensions, the language couldn't actually *do* anything, because it is at its
core just a language grammar.

-------
WHY!?!?
-------

I think there is room for another templating language.

Haml?  Coffekup?  Jade?  They don't seem pythonic to me.

Plain-Jane HTML?  Sure, if you want.  That is, I think, the best alternative to
plywood.

Even the great django template language is HTML made *nastier* by inserting
*additional markup*.  I looked at Jade and Haml as "yeah, you're getting there",
but they didn't nail it.

I'm unapologettically a DIY-er.  I think that sometimes wheels just need
re-inventing!  Plus, this gave me a chance to play with language grammars, which
I think are fun.  I'm using chomsky_ to build the plywood language parser.

----
TEST
----

::

    $ pip install pytest
    $ py.test

-------
LICENSE
-------

:Author: Colin Thomas-Arnold
:Copyright: 2012 Colin Thomas-Arnold <http://colinta.com/>

Copyright (c) 2012, Colin Thomas-Arnold
All rights reserved.

See LICENSE_ for more details (it's a simplified BSD license).

.. _LICENSE:    https://github.com/colinta/plywood/blob/master/LICENSE
.. _chomsky:   https://github.com/colinta/chomsky
