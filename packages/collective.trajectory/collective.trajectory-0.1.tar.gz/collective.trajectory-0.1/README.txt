Introduction
============

This product provides URL routing capability to Plone content. Powered by the 
awesome traject library by Martijn Faassen and based on a similar library called
megrok.traject.

Note: this is still a proof of concept, need more testing. 

What It Does
=============

Basically, this project allow your content to be a routing based app. For example,
with this product, you can have something like:

* site/folder/myApp - a traject enabled content, resolved through graph 
  traversal
* site/folder/myApp/models/1 - returns a SQLalchemy model object, resolved 
  through url routing

Enabling routing for content type
==================================

Hook this into ZCML::

    <adapter factory="collective.trajectory.components.Traverser"
           for="myproduct.content.mycontent.MyContent
                 zope.publisher.interfaces.IRequest"/>

where `myproduct.content.mycontent.MyContent` is the class of the content
type which will be the root of the URL routing.

Registering route patterns
===========================

Registering patterns is pretty much like how its supposed to be done in
normal traject. However, the model class will need to be inherited from
`collective.trajectory.components.Model`

    from collective.trajectory.components import Model
    from myproduct.content.mycontent import MyContent
    import traject

    class MyModel(Model):
        def __init__(self, item_id):
            self.item_id = item_id

    def factory(item_id):
        return MyModel(item_id)

    def arguments(obj):
        return {
            'item_id': obj.item_id
        }

    pattern = u'models/:item_id'
    traject.register(MyContent, pattern, factory)
    traject.register_inverse(MyContent, MyModel, pattern, arguments)


Additional Info
================

* The returned models acquire attributess from your MyApp object through 
  Acquisition, so that templates behave as it should, and portal tools 
  available through current context.
* Views are simply the standard plone browserviews, nothing fancy.
