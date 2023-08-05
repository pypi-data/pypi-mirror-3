=========================
HTML file editing support
=========================

This package contains support for editing HTML and XHTML inside a web
page using the FCKeditor as a widget.  This is a fairly simple
application of FCKeditor, and simply instantiates a pre-configured
editor for each widget.  There are no options to control the editors
individually.

In creating this, we ran into some limitations of the editor that are
worth being aware of.  Noting these as limitations does not mean that
other editors do any better; what's available seems to be a mixed bag.

- The editor only deals with what can be contained inside a <body>
  element; anything that goes outside that, including the <body> and
  </body> tags, get lost or damaged.  If there's any way to configure
  FCKeditor to deal with such material, it isn't documented.

- There's no real control of the HTML source; whitespace is not
  preserved as a programmer would expect.  That's acceptable in many
  use cases, but not all.  Applications should avoid using this widget
  if the original whitespace must be maintained.

Implementation problems
-----------------------

These are problems with the widget used to integrate FCKeditor rather
than problems with FCKeditor itself.  These should be dealt with.

- The width of the editor is hardcoded; this should be either
  configurable or the editor should stretch to fill the available
  space.  The sample uses of the FCKeditor don't seem to exhibit this
  problem, so it can be better than it is.

- The height of the editor should be configurable in a way similar to
  the configuration of the basic textarea widget.

Ideas for future development
----------------------------

These ideas might be interesting to pursue, but there are no specific
plans to do so at this time:

- Categorize the applications of the editor and provide alternate
  toolbar configurations for those applications.  There's a lot of
  configurability in the editor itself, so it can be made to do
  different things.

- Add support for some of the other fancy client-side HTML editors,
  and allow a user preference to select which to use for what
  applications, including the option of disabling the GUI editors when
  detailed control over the HTML is needed (or for luddite users who
  don't like the GUI editors).

  XINHA (http://xinha.python-hosting.com/) appears to be an
  interesting option as well, and may be more usable for applications
  that want more than editing of small HTML fragments, especially if
  the user is fairly HTML-savvy.

  HTMLArea (http://www.dynarch.com/projects/htmlarea/) may become
  interesting at some point, but a rough reading at this time
  indicates that XINHA may be a more reasonable route.

More information about FCKeditor
--------------------------------

- http://www.fckeditor.net/

- http://discerning.com/topics/software/ttw.html

- http://www.phpsolvent.com/wordpress/?page_id=330
