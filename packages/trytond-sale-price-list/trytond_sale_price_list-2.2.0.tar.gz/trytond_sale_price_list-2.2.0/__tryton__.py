#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name': 'Sale Pricelist',
    'name_bg_BG': 'Ценова листа',
    'name_de_DE': 'Verkauf Preislisten',
    'name_es_CO': 'Lista de Precios de Venta',
    'name_es_ES': 'Lista de precios de venta',
    'name_fr_FR' : 'Listes de prix de vente',
    'version': '2.2.0',
    'author': 'B2CK',
    'email': 'info@b2ck.com',
    'website': 'http://www.tryton.org/',
    'description': '''Define price list on party and sale order.
''',
    'description_bg_BG': '''Задаване на ценова листа за партньор и поръчка за продажба
''',
    'description_de_DE': '''Preislisten für Verkauf
    - Ermöglicht die Definition von Preislisten per Partei und Verkauf.
''',
    'description_es_CO': '''Precios de Venta
    - Define lista de precio de venta para un tercero y una orden de venta.
''',
    'description_es_ES': '''Lista de precios para ventas
    - Permite la definición de la lista de precios por tercero y orden de venta.
''',
    'description_fr_FR': '''Ajoute des listes de prix sur les tiers et sur les ventes.
''',
    'depends': [
        'ir',
        'party',
        'product_price_list',
        'sale',
    ],
    'xml': [
        'party.xml',
        'sale.xml',
    ],
    'translation': [
        'locale/bg_BG.po',
        'locale/cs_CZ.po',
        'locale/de_DE.po',
        'locale/es_CO.po',
        'locale/es_ES.po',
        'locale/fr_FR.po',
        'locale/nl_NL.po',
        'locale/ru_RU.po',
    ],
}
