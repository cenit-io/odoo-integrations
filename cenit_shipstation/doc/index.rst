ShipStation is a web-based software designed to help eCommerce retailers
process, fulfill, and ship their orders from all the most popular marketplaces
and shopping carts using all the top carriers.

The `Cenit.io`_ platform provides a collection that allows you to integrate with
Shipstation's API with ease.

Quick Installation Guide
========================

The only data you need to successfully install the Shipstation Integration
`addon`_ for Odoo are the ``API Key`` and ``API Secret`` related to your
Shipstation account. You can follow the steps described in the `addon`_
description if you are unsure on how to get those.

Usage
=====

Once installed, the `addon`_ features will allow you to send any data you want
as Shipstation Schemas. To do so, all you need is add `Data types` describing
how to transform your Odoo models into the Shipstation ones.

Let's see some examples, go and create a new `Data type`.

Orders
++++++

The most popular choice to map as Shipstation Orders are Odoo's
``stock.picking`` (also known as `Picking List`).

This model actually refers to product movements on your warehouses (both in and
out), so you will need to restrict them to those with ``picking_type_code`` set
as ``outgoing``. This is accomplished on the `Conditions` tab of the `Data type`
form. You may also consider to restrict to those which ``state`` is different
than ``draft``, as those are not yet confirmed.

But lets not get ahead of ourselves. For the `Name` we recommend using something
that'll let you know quickly what's the `Data type` about, something like
"Picking List as Shipstation Order". Make sure to select ``Picking List`` for
the model, ``Shipstation`` for the library and ``Order.json`` for the schema.

Now we are all for the mapping. Let's examine the ``Order.json`` schema
properties.

+ **orderId**: this is an internal property used by Shipstation and we won't be
  using it.

+ **orderNumber**: `string` - A user-defined order number used to identify an
  order.

  - **Schema property**: ``orderNumber``
  - **Model value**: ``id``
  - **Type**: ``Field``

+ **orderKey**: `string` - A user-provided key that should be unique to each
  order.

  - **Schema property**: ``orderKey``
  - **Model value**: ``name``
  - **Type**: ``Field``

+ **orderDate**: `string` - The date the order was placed.

  - **Schema property**: ``orderDate``
  - **Model value**: ``date``
  - **Type**: ``Field``

+ **orderDate**: `string` - The date the order was placed.

  - **Schema property**: ``orderDate``
  - **Model value**: ``date``
  - **Type**: ``Field``

+ **createDate**: also an internal property set by Shipstation.
+ **modifyDate**: as above.
+ **paymentDate**: at present this value is not obtainable, due to the internal
  structure of the ``Picking List``. Good thing is not mandatory.


+ **orderStatus**: `string` - The order's status. Possible values:
  "awaiting_payment", "awaiting_shipment", "shipped", "on_hold", "cancelled".

  Since the Picking ``state`` values are different from the Shipstation ones, we
  will use a Python code to translate them

  - **Schema property**: ``orderStatus``
  - **Model value**:
    ``{"cancel": "cancelled", "waiting": "awaiting_payment", "confirmed":
    "on_hold", "partially_available": "on_hold", "assigned":
    "awaiting_shipment", "done": "shipped"}.get(obj.state, "on_hold")``
  - **Type**: ``Python code``

  Note that we haven't mapped the "draft" ``state``, since we assume those will
  be restricted as stated at the beginning.

  Also note the use of the special variable `obj`, which refers to the actual
  object being serialized.

+ **customerId**: internal property set by Shipstation.

+ **customerUsername**: `string` - Identifier for the customer in the
  originating system. This is typically a username or email address.

  - **Schema property**: ``customerUsername``
  - **Model value**: ``{partner_id.login}``
  - **Type**: ``Default``

+ **customerEmail**: `string` - The customer's email address.

  - **Schema property**: ``customerEmail``
  - **Model value**: ``{partner_id.email}``
  - **Type**: ``Default``

+ **carrierCode**: `string` - The code for the carrier that is to be used (or
  was used) when this order is shipped(was shipped).

  - **Schema property**: ``carrierCode``
  - **Model value**: ``{carrier_id.name}``
  - **Type**: ``Default``

  Notice that this would require the additional ``delivery`` addon to be
  installed on your system, otherwise you might as well omit this from the
  mapping.

  Also, it is likely that the ``name`` field won't do the trick, so, if you can
  do so, maybe a more specific mapping can be made, check the next alternative
  example:

  - **Schema property**: ``carrierCode``
  - **Model value**:
    ``{"UPS": "ups", "FedEx": "fedex"}.get(obj.carrier_id.name, "ups")``
  - **Type**: ``Python code``

  or even something more generic:

  - **Schema property**: ``carrierCode``
  - **Model value**:
    ``obj.carrier_id.name.lower().replace(" ", "_").replace(".", "_")``
  - **Type**: ``Python code``

  just make sure all your carriers will be correctly processed in order to avoid
  crashes further down the road.

These are some of the possible mappings for `value` fields, but there are some
others that won't be mapped as easily.

For instance, the **billTo** and **shipTo** properties are complex `object`
types, for these we create their own `Data type`. So, for now, uncheck the
``Enabled`` tick, click the Save button and go and create a new `Data type`.

Address
-------

This new `Data type` will be representing a `Partner`'s address, so set the
model to ``res.partner`` (will most likely look like ``Partner``), the library
to ``Shipstation`` and the schema to ``address.json``. For the name choose
something like "Partner as Shipstation address" or anything you like.

We won't be restricting this `Data type` with ``Conditions`` since it is not
intended to trigger events on its own. On to the mappings:

+ **name**: `string` - Name of person.

  - **Schema property**: ``name``
  - **Model value**: ``name``
  - **Type**: ``Field``

+ **street1**: `string` - First line of address.

  - **Schema property**: ``street1``
  - **Model value**: ``street``
  - **Type**: ``Field``

+ **street2**: `string` - Second line of address.

  - **Schema property**: ``street2``
  - **Model value**: ``street2``
  - **Type**: ``Field``

+ **city**: `string` - City.

  - **Schema property**: ``city``
  - **Model value**: ``city``
  - **Type**: ``Field``

+ **state**: `string` - State.

  - **Schema property**: ``state``
  - **Model value**: ``{state_id.name}``
  - **Type**: ``Default``

  Note that most Odoo installations don't hold records for any State not in the
  US, so if it doesn't apply: don't use it.

+ **country**: `string` - Country Code. The two-character ISO country code is
  required.

  - **Schema property**: ``country``
  - **Model value**: ``{country_id.code}``
  - **Type**: ``Default``

+ **phone**: `string` - Telephone number.

  - **Schema property**: ``phone``
  - **Model value**: ``phone``
  - **Type**: ``Field``

That should do it for the moment. Save the `Data type` and head back to the one
for the Order.

----

+ **billTo**: `Address` - The recipients billing address.

  - **Schema property**: ``billTo``
  - **Model value**: ``partner_id``
  - **Type**: ``Model``
  - **Reference**: set this to the newly created `Data type` for the `Partner`'s
    address.
  - **Cardinality**: ``2one``

+ **shipTo**: `Address` - The recipients shipping address.

  - **Schema property**: ``shipTo``
  - **Model value**: ``partner_id``
  - **Type**: ``Model``
  - **Reference**: set this to the newly created `Data type` for the `Partner`'s
    address.
  - **Cardinality**: ``2one``

Another important complex property of the Order model refers to the list of
items to be shipped with the order (check out the **items** property). For that
one we will need to do something similar to what we did for the billing and
shipping addresses.

So save the `Data type` again (leave the ``Enabled`` tick unchecked) and let us
create a new one that maps Odoo's ``stock.move`` (you should see it as
``Stock Move``) items as Shipstation's ``order_item``.

Order Item
----------

As usual name your `Data type`, something like "StockMove as Shipstation
OrderItem" should be enough, for the model choose ``Stock Move``, set the
library to ``Shipstation`` and the schema to ``order_item.json``.

As with the partner's address above, this `Data type` should trigger no events,
so we won't set any conditions or triggers on it.

+ **orderItemId**: this is an internal property used by Shipstation and we won't
  be using it.

+ **lineItemKey**: `string` - An identifier for the OrderItem in the originating
  system.

  - **Schema property**: ``lineItemKey``
  - **Model value**: ``id``
  - **Type**: ``Field``

+ **sku**: `string` - The SKU (stock keeping unit) identifier for the product
  associated with this line item.

  - **Schema property**: ``sku``
  - **Model value**: ``{product_id.code}``
  - **Type**: ``Default``

+ **name**: `string` - The name of the product associated with this line item.

  - **Schema property**: ``name``
  - **Model value**: ``{product_id.name_template}``
  - **Type**: ``Default``

+ **quantity**: `number` - The quantity of product ordered.

  - **Schema property**: ``quantity``
  - **Model value**: ``product_qty``
  - **Type**: ``Field``

+ **unitPrice**: `number` - The sell price of a single item specified by the
  order source.

  - **Schema property**: ``unitPrice``
  - **Model value**: ``price_unit``
  - **Type**: ``Field``

That should be enough for the now. Save the `Data type` and let us return to the
Order one.

----

As you can see, the **items** property refers not to a single object, but rather
a list (expressed as an array), so we will be using a ``2many`` cardinality for
this one.

+ **items**: `OrderItem` - Array of purchased items.

  - **Schema property**: ``items``
  - **Model value**: ``move_lines``
  - **Type**: ``Model``
  - **Reference**: set this to the newly created `Data type` for the
    `Stock Move`.
  - **Cardinality**: ``2many``

With this you should have a fairly functional mapping of your ``Picking List``
to Shipstation's ``Order``, all that is left is to determine when to trigger the
sending of your data to Shipstation.

Go to the `Triggers` tab and add a new one. Select the `On creation or update`
option and that's all folks!

Check back the ``Enabled`` tick and save the `Data type`.

Testing
-------

In order to test the mappings go to the `Warehouse` tab on the top panel, and
under `All Operations` choose any `Delivery order`.

`Edit` it, modify something (probably adding a note would be right so not to
disturb the actual content on the delivery) and `Save` it. If it does matches
the `Conditions` for the `Data type`, you should able to see in `Cenit.io`_'s
data integrator, a record for that specific `Picking List`.


To be continued
===============

.. _Cenit.io: https://cenit.io
.. _addon: https://apps.openerp.com/apps/modules/8.0/cenit_shipstation/