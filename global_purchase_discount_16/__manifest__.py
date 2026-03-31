# -*- coding: utf-8 -*-
{
    "name": "Global Purchase Discount",
    "summary": """
        Aplica un descuento global en Órdenes y Solicitudes de Compra""",
    "description": """
        Permite aplicar un descuento global (%) sobre todas las líneas de una
        Solicitud de Cotización (RFQ) o una Orden de Compra (PO).
        El descuento se refleja en las líneas, en los totales y en el reporte impreso.
    """,
    "author": "NEOVERSA S.A. DE C.V.",
    "company": "NEOVERSA S.A. DE C.V.",
    "maintainer": "NEOVERSA S.A. DE C.V.",
    "website": "https://neoversa.net/",
    "category": "Inventory/Purchase",
    "version": "16.0.1.0.0",
    "depends": ["purchase"],
    "data": [
        "views/purchase_views.xml",
        "report/purchase_order_templates.xml",
    ],
    "images": [
        "static/description/banner.jpg",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
