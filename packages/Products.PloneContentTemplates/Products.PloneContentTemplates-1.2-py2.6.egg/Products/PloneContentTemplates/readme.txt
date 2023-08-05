Simple product to enable creating content from templates.  To use it,
install it through the Plone Control Panel.

Objects that are to be used as templates must have the keyword
content-template set, and after installing you'll be able to add from
templates using the Plone add menu.

An alternative approach to keywords is to customize the
pct_get_templates script and have it return all the objects from one
or more folders; see commented code in the script for details.

Should work with all Archetypes-based content which supports keywords.

It was developed for Plone 2.5.x and has been customized to work with
Plone 3 & Plone 4.  May not work for Plone 2.5 anymore but is assumed
to be working fine.

The old way of doing things was that the add from template option was
in the bottom of the add object dropdown - now it is an object button
instead, alongside copy, paste and so on.

Has English and Norwegian translations.

If you're not on Plone 4 / Python 2.6 you can download a Products
package from http://plone.org/products/plone-content-templates which
will be available shortly after the py2.6 egg.

Developed by Nidelven IT, http://www.nidelven-it.no
