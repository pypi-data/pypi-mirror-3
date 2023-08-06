Creation of your Columns mapping
********************************

Base mapping structure
======================

Model of the skeleton::

    {
        `model`: [
           {
               `field`: (`column`, `callback`, `search`),
           }
        ],
        `REL_XX::model`: {
            ...
        },
    }


Field declaration arguments
===========================

.. rubric:: model (str)

OpenERP osv model name (`res.partner.address` for example).

.. rubric:: field (str)

OpenERP field name (`partner_id` for example).

Special cases::

    SKIP
        Skip line if callback return True, nothing if False

    REPLACE
        Replace processed line by an other if callback return an int
        if tuple (`line`, `column`) returned, will replace actual line
        by value at %line% in %column%

.. rubric:: column (single int or list)

Columns number from the CSV file. If a list is provided, a concatenation will
be used.

.. rubric:: callback (lambda or None)

Function called with get back value from `column` index.

.. rubric:: REL_XX::model (str)

Name of the key into columns mapping which will be consider as a per-relation
object to import, it must start with `REL_X:` where X is a unique id
(not length limited) inside the mapping.


Creating relations between models
=================================

`csv2oerp` also allows you to virtually create the relationship that fields
would have between them.

A `res.partner` object has a relation to `res.partner.address`. If these two
objects's field are on the same line (in the CSV file), then you can define a
relationship directly into the mapping.

A simple relationship between `res.partner` and `res.partner.address`::

    +-------------+                                        +-------------------+
    | res.partner |                                        |res.partner.address|
    +-------------+                                        +-------------------+
    |             |                                        |                   |
    |             | address                     partner_id |                   |
    |             +----------------------------------------+                   |
    |             | *                                    1 |                   |
    |             |                                        |                   |
    +-------------+                                        +-------------------+

It will looks like this in the mapping::
    
    'res.partner.address': [ 
        {
            'partner_id':   (None, 'REL_adh::res.partner', True),
        },
    ],
    'REL_adh::res.partner': {
        'address': () ..
    }


