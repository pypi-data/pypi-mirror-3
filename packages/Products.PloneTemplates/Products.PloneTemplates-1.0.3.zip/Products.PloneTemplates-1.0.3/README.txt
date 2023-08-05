Overview
========

PloneTemplates is a product that allows you to make templates like you
know them from other applications such as Word of Excel (don't confuse them
with zope page templates, it's totally unrelated!!).

Usage is very simple. Suppose you have to create a Page many times with
every time the same basic content. Instead of manually copying and pasting another
Page that acts as the template, this product does it all for you with an
easy to use user-interface.

First you create a Template object somewhere in your portal. Just like any other
object using the Add new menu. This Template object
is in fact a folder that can contain any other portal object (one or more!).
In our example, we create a Page inside this Template. We edit this Page and
we write its boiler plate body text (and whatever else you wish to preset)
and you save the Page. Then you can write optional usage instructions in
the Template object (edit tab) itself. This is all you need to do to define
the template. Of course you can also copy/paste any existing objects inside the
Template.

Now, the final step is to go to a place in the portal (usually a Folder) where
we wish to enable this new Template so users can instantiate it.
So, we edit the Folder and we click on the templates link (schemata/fieldset)
at the top of the edit form. There we can use the Browse button to locate
the newly created Template in the portal. (Here we can also choose if this
Template is added to Templates already registered in higher levels in the
Folder hierarchy).

So, we select the Template we just created and we press Save. From then on,
a new drop-down menu called 'template's appears next to the Add new menu
in the context of this Folder and in any of it's subfolders. This menu contains
the Templates the user can pick from.

So.. let this get to you for a few seconds...

So, to summarize, you can create a Template object, put in there whatever
you want, register this Template anywhere in a folderish object in the portal
and from then on you can consider this Template (actually it's content) as a new addable
object (or collection of objects)? Yes. That's all there is to it!

Possibilities are endless. You can predefine all kinds of Issues that you
want to have available in an Issue Tracker, you can predefine entire folder
structures and put them in a Template like a project folder you want for
each new project. Create a Page that holds the structure for a customer description
etc etc.

Additional notes, read carefully!
---------------------------------

After a Template is instantiated by a user somewhere, the focus is set to the
first object that will be created. Also, the icon shown in the templates
drop-down menu is from the first contained object inside the Template object.

Due to the way the current version of Archetypes deals with references, you cannot
have Templates registered to a Folder that is INSIDE another Template.
PloneTemplates uses references to register a Template to a Folder and
references are lost when you copy/paste something. I know.. it sux and
we know this for ages.

You can control if the user will get to see an intermediate page with the
usage information when he picks a template from the menu.
This is a switch in the Template edit form.

Workflow states are reset to their defaults when a templates gets instantiated.
(This happens for everything that get's copied and pasted and this is not
different).

This product comes with a tool that also allows you to instantiate templates
from script (Use the source Luke!) and you can even add a post-process function
that can do something with the instantiated objects. I used that to create
member areas with lots of stuff in there like subfolders, personal blogs etc etc.

There is a mixin-class to make your product also template aware so you can
register Templates and have the templates menu. Add this in
your product class::

  from Products.PloneTemplates.TemplateSchema import PloneTemplatesMixinSchema

and do this with your schema::

  schema = schema + PloneTemplateMixinSchema

Additionally, this product monkeypatches ATFolder to make it template
aware (add a few fields to the schema). In config.py you can see how this
is done and you can add other types as well in a similar fashion. Or,
you can empty the list typesToPatch to not path the Folder type. So, out of
the box, this product will only allow Folders to have a templates drop-down menu.
In other words, if you have, let's say an Issue tracker product that also needs to use
templates, you have to either patch it (inject some fields) or use the mixin schema.
