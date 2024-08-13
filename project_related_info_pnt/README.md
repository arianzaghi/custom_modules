Project Resource Quick Access
=============================

This module adds a series of buttons on the project view to quickly view and access the different project-associated resources such as sale orders, purchase orders, invoices, and stock pickings. The buttons include mini indicators showing the number of records, and clicking on them takes you to a tree view of the chosen resource.

**Table of Contents**

.. contents::
   :local:

Configuration
=============

None.

Usage
=====

Standard Odoo functionality. After installation, the buttons will appear in the project view, allowing for quick navigation to associated resources.

Resource Linking Details

1. **Sale Orders**:
   - Linked by default to sale orders that have the project's analytic account in the sale order header.
2. **Sale Invoices**:
   - Linked by default to sale invoices that have lines containing the project's analytic account.
3. **Purchase Orders**:
   - Linked by default to purchase orders that have lines containing the project's analytic account.
4. **Purchase Invoices**:
   - Linked by default to purchase invoices that have lines containing the project's analytic account.
5. **Outgoing Pickings**:
   - Linked by default to pickings originating from a sale with the project's analytic account.
6. **Incoming Pickings**:
   - Linked by default to pickings originating from a purchase with the project's analytic account.

Known Issues
============

There are no known problems at present.

Credits
=======

### Authors
~~~~~~~~~~~

* `Punt Sistemes <https://www.puntsistemes.es>`__

### Contributors
~~~~~~~~~~~~~~~~

* `Arian Zaghi <arianzaghi@puntsistemes.es>`__:

### Maintainers
~~~~~~~~~~~~~~~

Maintained by `Punt Sistemes <https://www.puntsistemes.es>`__.

.. image:: /custom_module/static/img/your-company-logo.png
   :alt: Your Company
   :target: https://www.yourcompanywebsite.com
