from odoo import api, fields, models


class PntSearchSQLdMixin(models.AbstractModel):
    _name = "sql.search.mixin"
    _description = "Search for field matching records within a model and with optional domain"

    def _get_disctinct_ids_with_field(
        self, model, domain, field_name_to_search, field_filter_id
    ):
        obj = self.env[model]
        table_name = obj._table
        query = obj._search(domain)
        query.add_where(
            f'"{ table_name}"."{ field_name_to_search}" ? %s', [str(field_filter_id)]
        )
        query.order = f'"{ table_name}"' + '."id"'
        query_string, query_param = query.select('DISTINCT '+f'"{ table_name}".id')

        self._cr.execute(query_string, query_param)
        return [pol.get("id") for pol in self._cr.dictfetchall()]
