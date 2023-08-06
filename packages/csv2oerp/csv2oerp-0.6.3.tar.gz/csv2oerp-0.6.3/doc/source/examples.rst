.. _examples:

*************
Some examples
*************

Partners importation
====================

.. csv-table:: customers_suppliers.csv

   :header: "name","customer","supplier","email","country","city","comment","website","phone"
    
    "Agrolait","1","0","s.l@agrolait.be","BE","Wavre","","www.agrolait.com","3281588558"
    "ASUStek","0","1","info@asustek.com","TW","Taiwan","","www.asustek.com","+1 64 61 04 01"
    "Axelor","1","1","info@axelor.com","FR","Champs sur Marne","","www.axelor.com/","+33 1 64 61 04 01"
    "BalmerInc S.A.","1","0","info@balmerinc.be","BE","Bruxelles","","www.balmerinc.com","(+32)2 211 34 83"
    "Bank Wealthy and sons","1","0","a.g@wealthyandsons.com","FR","Paris","","www.wealthyandsons.com/","3368978776"
    "Camptocamp","1","1","","CH","Lausanne","","www.camptocamp.com","+41 21 619 10 04"
    "China Export","1","0","zen@chinaexport.com","CN","Shanghai","","www.chinaexport.com/","+86-751-64845671"
    "Distrib PC","0","1","info@distribpc.com","BE","Namur","","www.distribpc.com/","+32 081256987"
    "Dubois sprl","1","0","m.dubois@dubois.be","BE","Brussels","Sprl Dubois would like to sell our bookshelves but they have no storage location, so it would be exclusively on order","http://www.dubois.be/",""
    "Ecole de Commerce de Liege","1","0","k.lesbrouffe@eci-liege.info","BE","Liege","","www.eci-liege.info//","+32 421 52571"
    "Elec Import","0","1","info@elecimport.com","BE","Brussels","","","+32 025 897 456"
    "Eric Dubois","1","0","e.dubois@gmail.com","BE","Mons","","","(+32).758 958 789"
    "Leclerc","1","0","marine@leclerc.fr","","Brest","","","+33-298.334558"
    "Maxtor","0","1","info@maxtor.com","CN","Hong Kong","","","+11 8528 456 789"
    "Mediapole SPRL","1","0","","BE","Louvain-la-Neuve","","http://mediapole.net","(+32).10.45.17.73"
    "NotSoTiny SARL","1","0","","BE","Namur","","notsotiny.be","(+32).81.81.37.00"
    "Seagate","1","1","info@seagate.com","US","Cupertino","","","+1 408 256987"
    "SmartBusiness","1","0","contact@smartbusiness.ar","AR","Buenos Aires","","","(5411) 4773-9666 "
    "Syleam","1","0","contact@syleam.fr","FR","Alencon","","www.syleam.fr","+33 (0) 2 33 31 22 10"
    "Tecsas","1","0","contact@tecsas.fr","FR","Avignon CEDEX 09","","","(+33)4.32.74.10.57"
    "The Shelve House","1","0","","FR","Paris","","",""
    "Tiny AT Work","1","0","info@tinyatwork.com","US","Boston","","www.tinyatwork.com/","+33 (0) 2 33 31 22 10"
    "Université de Liège","1","0","martine.ohio@ulg.ac.be","","Liège","","http://www.ulg.ac.be/","+32-45895245"
    "Vicking Direct","1","1","","BE","Puurs","","vicking-direct.be","(+32).70.12.85.00"
    "Wood y Wood Pecker","0","1","","FI","Kainuu","","woodywoodpecker.com","(+358).9.589 689"
    "ZeroOne Inc","1","0","","BE","Brussels","","http://www.zerooneinc.com/",""

Importation script::

    >>> import csv2oerp
    >>> from csv2oerp.fields import Column, Relation, Custom
    >>> from csv2oerp.callbacks import get_id, to_boolean

    >>> # Set OpenERP configuration access
    >>> csv2oerp.connect('localhost', 8069, 'admin', 'admin', 'dbname')

    >>> customers_suppliers = csv2oerp.Import()
    >>> customers_suppliers.set_input_file('customers_suppliers.csv')
    >>> customers_suppliers.set_mapping({
    ...     'res.partner': [ 
    ...             {
    ...                 'name':         Column(0, search=True),
    ...                 'customer':     Column(1, to_boolean()),
    ...                 'supplier':     Column(2, to_boolean()),
    ...                 'email':        Column(3),
    ...                 'city':         Column(5),
    ...                 'comment':      Column(6),
    ...                 'website':      Column(7),
    ...                 'phone':        Column(8),
    ...             },
    ...         ],
    ...     })

    >>> # Finally start the importation process
    >>> customers_suppliers.start()

