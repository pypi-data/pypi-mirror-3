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
Plone 3 as well and presumably works with Plone 4 and may not work for
Plone 2.5 anymore.

The old way of doing things was that the add from template option was
in the bottom of the add object dropdown - now it is an object button
instead, alongside copy, paste and so on.

Has English and Norwegian translations.

Developed by Nidelven IT, http://www.nidelven-it.no
