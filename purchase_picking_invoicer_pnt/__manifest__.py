{
    "name": "Purchase invoices from picking",
    "version": "16.0.1.0.0",
    "category": "Accounting",
    "website": "https://www.puntsistemes.es",
    "author": "Punt Sistemes",
    "summary": "Create purchase invoices from picking",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move.xml",
        "views/stock_picking.xml",
        "views/stock_picking_type.xml",
        "views/pnt_stock_picking_supplier.xml",
    ],
}
