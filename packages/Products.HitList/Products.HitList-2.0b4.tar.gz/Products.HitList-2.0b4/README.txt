Introduction
============

Products.HitList provides a simple hit-list functionality for Plone. Users may
add objects of specific content types to their HitList and remove them if no
longer needed. The current hit-list of a user may be displayed in a portlet or
on a specific view.


Integration
===========

By default the hit-list behavior is not activated for any content type. The
functionality is bound to a marker interface::

    Products.HitList.interfaces.IHitListContent

Objects implementing this interface may be added to the hit-list. Activate the
behavior for existing content types may be done by subclassing or preferable
by using the five:implements directive in zcml.


Example
=======

By using the following zcml directive the hit-list functionality is activated for
Documents::

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:five="http://namespaces.zope.org/five">
      
        <five:implements
            class="Products.ATContentTypes.content.document.ATDocument"
            interface="Products.HitList.interfaces.IHitListContent"
            />
    
    </configure>

