grokui.base -- Base components for Grok UI
******************************************

``grokui.base`` is a base layer to build a zope instance-level set of
utilities. The package provides a collection of easy-to-use components
that will allow you to build your own configuration or admin panels.
`grokui.base` provides the components that should be used by other
`grokui` packages to plug into a coherent layout.

Using `grokui.base` we can provide different UI parts that can be used
indenpendently from each other, for example a ZODB browser or a
general admin panel to manage local Grok applications. It is up to the
admins to decide what grok UI parts they want to have installed.

In general, `grokui.base` provides viewlets, menus, layouts and a
special namespace for use by other components.
