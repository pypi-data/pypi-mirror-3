Introduction
============

Our vision for uwosh.northstar is as a complete through-the-web (TTW)
tool for generating workflow applications, ie. a custom content type
combined with an assigned custom workflow.  

Right now it adds a control panel entry ``Workflow Manager`` where you
can access the workflow tool. It also adds a ``Workflow App Generator``
control panel entry where you can generate your workflow app products.

Creating content types is easily done by using Dexterity. The tool will
simply dump your dexterity content type. If you can not use dexterity,
the tool also supports using PloneFormGen as your modeling tool in which
it'll create a corresponding Archetype for the PloneFormGen form you've
created.

uwosh.northstar is strictly for add-on product workflows and content types.
By design, the tool cannot be used to edit default Plone workflows.

It provides all the functionality you need to manipulate workflows
easily through the web, using an AJAX-powered interface and to generate the
products of the content types and workflows you've created TTW.


You can take a look at the new video demonstrating the workflow editor
http://www.youtube.com/watch?v=DO8RhPo9YNc


Tested with
-----------
* Firefox
* Google Chrome
* Safari
* Opera
* IE8


Installation
============

Just add `uwosh.northstar` to your buildout eggs sections and then
install the "North* " product in the add/remove products control
panel.

In older versions of Plone, you might need to add
plone.app.jquerytools to your zcml slug section of your buildout also.


Workflow App Generation with PloneFormGen
-----------------------------------------

>>> eggs = 
>>>   ...
>>>   Products.PloneFormGen
>>>   ZopeSkel
>>>   Paste
>>>   PasteScript


Workflow App Generation with Dexterity
---------------------------------------

>>> eggs = 
>>>   ...
>>>   plone.app.dexterity
>>>   ZopeSkel
>>>   zopeskel.dexterity
>>>   Paste


Graphing
--------

One feature of North* is that it can create a Diagram of the workflows 
you create TTW. 

The inspiration for this piece was pretty much taken from DCWorkflowGraph.

In order to enable this feature, you'll need to install the Graphviz library.
Information can be found at http://www.graphviz.org

Once you've built Graphviz and have installed it, make sure the "dot"
executable it creates is in your PATH, e.g.

export PATH=$PATH:/usr/local/bin

assuming "make install" placed the Graphviz executables into
/usr/local/bin. You can test that your PATH is set correctly if "which
dot" finds the "dot" executable.

Then restart your Zope or ZEO client. The next time you are looking at
a custom workflow in Workflow Manager, you should see a new "Diagram"
button. When you click on it, it generates a GIF depicting the
workflow's states and transitions.


Windows Compatibility
---------------------

We have encountered a problem on Windows in which the Workflow App
Generator creates a tar file but it doesn't contain everything
expected.  We suspect either a Python or paster problem.



Produced by Secret Laboratory Number 1 at UW Oshkosh.

