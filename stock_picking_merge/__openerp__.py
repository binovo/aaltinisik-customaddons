# -*- coding: utf-8 -*-
# Copyright 2018 Ahmet Altinisik
# Copyright 2018 Binovo IT Human Project SL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Merge",
    "summary": """
        Stock Picking Merge.
    """,
    "version": "8.0.1.0.0",
    "website": "http://ahmet.altinisik.net",
    "category": "Warehouse Management",
    "author": "Kiran Kantesariya, Ahmet Altinisik",
    "depends": [
        "stock"
    ],
    "data": [
        "security/res_groups.xml",
        "wizard/picking_merge_wiz_view.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
    "auto_install": False,
}
