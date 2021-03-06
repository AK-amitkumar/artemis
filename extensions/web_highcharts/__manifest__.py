# -*- coding: utf-8 -*-
{
    "name": """Highchart odoo 10""",
    "summary": """Chart View odoo 10""",
    "category": "Hidden",
    "images": [],
    "version": "1.0.1",
    "author": "Suhendar",
    "website": "https://bdo.co.id",
    "license": "AGPL-3",
    "depends": [
        "web",
    ],
    "data": [
        'views/web_highcharts.xml',
    ],
    "qweb": [
        'static/src/xml/*.xml',
    ],
    "demo": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
    "application": False,
}