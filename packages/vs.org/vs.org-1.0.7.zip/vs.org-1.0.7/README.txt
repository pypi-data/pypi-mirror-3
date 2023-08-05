vs.org
======

Using vs.org almost any organization including its institutions, departments
and employees may be represented within a Plone site. Even complex
organizational structures can be made accessible and displayed, structered by
business area, specialization and region.

Features
========

vs.org offers the following content types:

Institution
-----------

Telephone numbers
`````````````````

An institution can hold an arbitrary number of telephone numbers. The
vocabulary for descriptions can be assigned such that common declarations
``telephone``, ``fax`` and ``mobile`` can be used, as well as ``reception``,
``ward`` and others.  Each number may be marked as `externally visible`. This
way it is possible to administer internal numbers in vs.org, even if the page
for the institution is published.

Address
```````

Any number of addresses may be assigned to an institution. Provide details of
street address, P.O. box, a delivery address and others.  The first address
given is used to generate a map using Google maps services. If the automatic
mapping is not precise enough you may provide geo coordinates.  With the
generated map you may also display directions in RichText. An optional
photograph or image of the institution is also helpful.

Business area
`````````````

Any institution may show its business area.  Editors may administer the
business area vocabulary.

Employees
`````````

Employees of an institution are referenced from entries in an employee folder.
The order of employees is freely assignable. 


Department
----------

A department can hold an arbitrary number of telephone numbers, described by
custom vocabulary. Each number may be marked as `externally visible`. 

Building section / floor / room no.
```````````````````````````````````

Departments are always part of an institution, so have no address of their own.
Instead you provide building section, floor or room number details.

Specialization
``````````````

Any department may be assigned a specialization.


Employee
--------

Any employee can be described using

- Position
- Salutation
- Title (academic or other)
- Firstname
- Surname
- Telephone numbers
- Email
- URL
- Portrait
- Notes

Again, any number of telephone number is possible. Each may carry arbitrarily
assigned vocabulary for description.  For each employee a business card in
vcard format is generated that can be imported into address books and contacts.


Views
-----

The institution homepage view makes specific institutions, departments
accessible using their business areas, specializations and regions.


Portlets
--------


Institution portlet
```````````````````

This portlet shows name and image of the institution, the addresses linking to
Google maps, the telephone numbers and employees.


Department portlet
``````````````````

Very similar to the institution portlet, showing building section, floor and
room number instead of an address.


Similar institutions, similar departments
`````````````````````````````````````````

Shown in the context of an institution, this portlet provides other
institutions sharing the same business area. In the same way, a portlet shows
other departments having the same specialization.

Employee search
---------------

Searching for employees is using the employee's surnames. This search can be
adapted to specific institutions.


Use cases
=========

Websites of organizations having a complex organizational structure.

Intranets and extranets that are used by employees and/or partner organizations
who need to find contact information quickly.


References
==========

- Immanuel Diakonie Group 



Requirements
============

- Plone 4
- Products.ATVocabularyManager
- Products.DataGridField
- Products.MasterSelectWidget
- pycountry


Requirements
============

* tested with Plone 4.0.X
* no support for Plone 3.X

Licence
=======

``vs.org`` is published under the GNU Public Licence V 2 (GPL 2)

Authors
=======

| Andreas Jung
| info@zopyx.com
| www.zope.com
|
| Veit Schiele
| kontakt@veit-schiele.de
| www.veit-schiele.de
|
| Carsten Raddatz
| carsten.raddatz@veit-schiele.de

Credits
=======

*  Anne Wather (Original author)

