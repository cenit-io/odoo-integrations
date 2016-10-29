# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2014 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Recipe_and_grocery_list_api_v_partner Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': '#Documentation

This is the documentation for the partner endpoint of the BigOven Recipe and Grocery List API.

The update brings with it Swagger-based documentation. [Swagger](http://swagger.io) is an emerging standard for describing REST-based APIs, and with this Swagger-compliant endpoint (above), you can make ready-to-go interface libraries for your code via [swagger-codegen](https://github.com/swagger-api/swagger-codegen). For instance, it's easy to generate libraries for Node.js, Java, Ruby, ASP.NET MVC, jQuery, php and more!

You can also try out the endpoint calls with your own api_key right here on this page. Be sure to enter your api_key above to use the "Try it out!" buttons on this page.

##Start Here

Developers new to the BigOven API should start with this version, not with the legacy API. We'll be making improvements to this API over time, and doing only bug fixes on the v1 API.



To pretend you're a BigOven user (for instance, to get your recently viewed recipes or your grocery list), you need to pass in Basic Authentication information in the header, just as with the v1 API. We do now require that you make all calls via https. You need to pass your api_key in with every call, though this can now be done on the header (send a request header "X-BigOven-API-Key" set to your api_key value, e.g., Request["X-BigOven-API-Key"]="your-key-here".)

##Migration Notes

For existing partners, we encourage you to [migrate](http://api2.bigoven.com), and while at this writing we have no hard-and-fast termination date for the v1 API, we strongly prefer that you migrate by January 1, 2017. While the changes aren't overly complex, there are several breaking changes, including refactoring of recipe search and results and removal of support for XML. This is not a simply plug-and-play replacement to the v1 API. With respect to an exclusive focus on JSON, the world has spoken, and it prefers JSON for REST-based API's. We've taken numerous steps to refactor the API to make it more REST-compliant. Note that this v2 API will be the preferred API from this point onward, so we encourage developers to migrate to this new format. We have put together some [migration notes](/web/documentation/migration-to-v2) that we encourage you to read carefully.

##Photos

See our [photos documentation](http://api2.bigoven.com/web/documentation/recipe-images). 

For more information on usage of this API, including features, pricing, rate limits, terms and conditions, please visit the [BigOven API website](http://api2.bigoven.com).',
    'description': """
        Odoo - Recipe_and_grocery_list_api_v_partner integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'view/config.xml',
        'view/wizard.xml'
    ],
    'installable': True
}
