Introduction
============

slc.autocategorіze enables you to let the objects created inside a folder
automatically receive the same categories metadata as the folder itself.

The contained objects receive the same categorization of the folder when they 
are created. The effect is not retroactive though, and when you change the
categories on a folder, the contained objects will not be re-categorized.

How it works:
-------------
This product add a boolean field 'autoCategorizeContent' on all BaseFolder
based folders. When this field is set to true for a certain folder, all 
the objects created in that folder will receive the folder's categories (the
value of the 'subject' field) in addition to any categories manually set on the
object.

The 'autoCategorizeNewContent' and 'recursiveAutoCategorization' fields are added 
to the BaseFolder schema via a schema-extender adapter. You can override this 
adapter in your own product to be applicable to another Archetype class if
necessary*. 

*See slc.autocategorize.configure.py*
 
How To Use (Simple DocTests):
=============================

First we create a folder whose children we want to be categorized
automatically:

    >>> self.folder.invokeFactory('Folder', 'documents')
    'documents'
    >>> folder = self.folder._getOb('documents')

To enable the auto-categorization feature, we must set the 'autoCategorizeContent' 
field on the parent folder. 

This is a field added via schema-extension, so we cannot use an Archetypes
generated mutator.

    >>> folder.Schema().get('autoCategorizeNewContent').set(folder, True)

Let's categorize our folder:

    >>> folder.setSubject(['foo', 'bar', 'baz'])

We now create a document inside this folder and test whether it has
been given the same 'subject' values:

    >>> folder.invokeFactory('Document', 'document1')
    'document1'
    >>> d1 = folder.get('document1')

Normally, when you created an Archetypes object in Plone, the
ObjectInitializedEvent is called. slc.autocategorize uses this event to know
when a new object has been created. 

Here we have to do it manually:

    >>> from zope import event
    >>> from Products.Archetypes.event import ObjectInitializedEvent
    >>> event.notify(ObjectInitializedEvent(d1))

Now we test that the folder's categories have been added:

    >>> d1.Subject()
    ('foo', 'bar', 'baz')

Let's also make sure that existing categories on a document are not deleted
when it receives new ones from it's parent folder. We also want to be sure that
when the child object already has one of the categories of the parent, that
it is not duplicated during the autocategorization process:

First we create the new object:

    >>> folder.invokeFactory('Document', 'document2')
    'document2'

Then we set the categories:

    >>> d2 = folder.get('document2')
    >>> d2.setSubject(['baz', 'buz'])

Then we call the event to notify slc.autocategorized that an object was created
(in Plone this happens automatically):

    >>> from Products.Archetypes.event import ObjectInitializedEvent
    >>> event.notify(ObjectInitializedEvent(d2))

Let's test that the categories are as expected:

    >>> d2.Subject()
    ('baz', 'buz', 'foo', 'bar')

Finally, we test that the 'recursive autocategorіzation' feature works.
First we create a subfolder and inside that folder another document:

    >>> folder.invokeFactory('Folder', 'sub-folder')
    'sub-folder'
    >>> subfolder = folder.get('sub-folder')
    >>> subfolder.invokeFactory('Folder', 'document3')
    'document3'

Again we have to call the appropriate event:

    >>> d3 = subfolder.get('document3')
    >>> event.notify(ObjectInitializedEvent(d3))

And now we make sure that now categories were set yet, since the recurse
feature was not yet activated:

    >>> d3.Subject()
    ()

Ok, so let's now activate recursion:

    >>> folder.Schema().get('recursiveAutoCategorization').set(folder, True)

Then we create a new document:

    >>> subfolder.invokeFactory('Folder', 'document4')
    'document4'
    >>> d4 = subfolder.get('document4')
    >>> event.notify(ObjectInitializedEvent(d4))

and test that the categories were set correctly:

    >>> d4.Subject()
    ('foo', 'bar', 'baz')



