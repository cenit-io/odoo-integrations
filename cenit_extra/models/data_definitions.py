#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  data_definitions.py
#
#  Copyright 2015 D.H. Bahr <dhbahr@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import logging
import simplejson

from openerp import models, fields, api


_logger = logging.getLogger(__name__)


class CenitDynamicMapper(models.TransientModel):
    _name = "cenit.dynamic.mapper"

    @api.model
    def __match_linetype(self, field):
        rc = {}
        if field.ttype not in (u"many2one", u"many2many", u"one2many"):
            rc.update({"line_type": "field"})
        else:
            domain = [('model', '=', field.relation)]
            candidates = self.search(domain)

            if candidates:
                rc.update({
                    "line_type": "model",
                    "reference": candidates[0],
                    "line_cardinality": "2%s" % (field.ttype.split("2")[1])
                })
            else:
                rc.update({
                    "line_type": "reference",
                    "line_cardinality": "2%s" % (field.ttype.split("2")[1])
                })

        return rc

    @api.model
    def __match_schematype(self, line_type):
        return {
            u"datetime": {"type": "string", "format": "date-time"},
            u"float": {"type": "number"},
            u"integer": {"type": "integer"},
            u"boolean": {"type": "boolean"},
        }.get(line_type, {"type": "string"})

    @api.model
    def _update_schema_properties(self, values):
        schema = simplejson.loads(self.schema.schema)

        schema['properties'].clear()
        schema['properties'].update(values)

        return simplejson.dumps(schema)

    @api.model
    def _guess_value_from_name(self, name):
        if name.endswith("_id"):
            return name[:-3]
        return name

    @api.model
    def _sluggify(self, string):
        return "_".join(string.lower().split())

    @api.model
    def _camelize(self, slug):
        return "".join([s.capitalize() for s in slug.split("_")])

    @api.model
    def schema_from_datatype(self, data_type):
        schema = data_type.schema
        lines = []
        if not schema:
            schema = {
                "title": vals["name"],
                "type": "object",
                "properties": {},
            }

            odoo_fields = (
                u"create_date",
                u"create_uid",
                u"write_date",
                u"write_uid",
            )

            model_pool = self.env['ir.model']
            model = model_pool.browse(vals['model'])

            if vals.get('lines', False):
                for _,__,line in vals['lines']:
                    if _ == 0:
                        candidates = [
                            x.name for x in model.field_id if x.name == line[
                                'name'
                            ]
                        ]

                        if not candidates:
                            vals['lines'].remove([_,__,line])

            for f in model.field_id:
                if f.name not in odoo_fields:

                    values = {
                        'name': f.name,
                        'value': self._guess_value_from_name(f.name)
                    }

                    values.update(self.__match_linetype(f))
                    flag = -1
                    pos = 0
                    if vals.get('lines', False):
                        for line in vals['lines']:
                            if line[2]['name'] == values['name']:
                                flag = pos
                                break
                            else:
                                pos += 1

                    if vals.get('lines', False) and (flag < 0):
                        continue

                    if values['line_type'] == "field":
                        schema['properties'].update({
                            values['value']: self.__match_schematype(f.ttype)
                        })

                    elif values['line_type'] == "reference":
                        mod = model_pool.search([('model', '=', f.relation)])[0]
                        field_names = [ x.name for x in mod.field_id ]
                        name = "name" in field_names

                        if name:
                            data = {}

                            if values['line_cardinality'] == "2many":
                                data.update({
                                    "type": "array",
                                    "items": self.__match_schematype("string")
                                })

                            else:
                                data.update(self.__match_schematype("string"))

                            schema['properties'].update({
                                values['value']: data
                            })
                        else:
                            continue

                    elif values['line_type'] == "model":
                        data = {}
                        ref = values.pop("reference")
                        values.update({"reference": ref.id})

                        if values['line_cardinality'] == "2many":
                            data.update({
                                "type": "array",
                                "referenced": True,
                                "items": {
                                    "$ref": "%s.json" % (ref.cenit_root,)
                                }
                            })

                        else:
                            data.update({
                                "referenced": True,
                                "$ref": "%s.json" % (ref.cenit_root,)
                            })

                        schema['properties'].update({
                            values['value']: data
                        })

                    else:
                        schema['properties'].update({
                            values['name']: self.__match_schematype(f.ttype)
                        })

                    if not vals.get('lines', False):
                        lines.append(values)
                    else:
                        if not vals['lines'][flag][2].get('value', False):
                            vals['lines'][flag][2].update({
                                'value': values.get('value', False)
                            })

                        if not vals['lines'][flag][2].get('line_type', False):
                            vals['lines'][flag][2].update({
                                'line_type': values.get('line_type', False)
                            })

                        if not vals['lines'][flag][2].get('reference', False):
                            vals['lines'][flag][2].update({
                                'reference': values.get('reference', False)
                            })

                        if not vals['lines'][flag][2].get(
                            'line_cardinality', False
                        ):
                            vals['lines'][flag][2].update({
                                'line_cardinality': values.get(
                                    'line_cardinality', False
                                )
                            })

            #~ vals.update({'schema': simplejson.dumps(schema)})

            val_lines = []
            for line in lines:
                val_lines.append([0, False, line])

            if not vals.get('lines'):
                vals.update({'lines': val_lines})
            else:
                vals['lines'].extend(val_lines)

            schema = self.env['cenit.schema'].create({
                'library': vals['library'],
                'uri': "%s.json" % (self._sluggify(vals['name'])),
                'schema': simplejson.dumps(schema)
            })
            vals.update({
                'schema': schema.id
            })
