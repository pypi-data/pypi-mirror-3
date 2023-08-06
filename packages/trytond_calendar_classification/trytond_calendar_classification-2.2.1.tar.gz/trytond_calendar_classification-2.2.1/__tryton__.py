# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name' : 'Calendar Classification',
    'name_bg_BG' : 'Класификация за календар',
    'name_de_DE' : 'Kalender Klassifikation',
    'name_es_CO' : 'Clasificación del calendario',
    'name_es_ES' : 'Clasificación del calendario',
    'name_fr_FR' : 'Classification calendrier',
    'name_ru_RU' : 'Классификация по календарю',
    'version' : '2.2.1',
    'author' : 'B2CK',
    'email': 'info@b2ck.com',
    'website': 'http://www.tryton.org/',
    'description': 'Handle classification of event',
    'description_bg_BG': 'Добавя класификация на събития в CalDAV',
    'description_de_DE' : '''
    Fügt Unterstützung für die Klassifikation von Terminen in CalDAV hinzu.
''',
    'description_es_CO': 'Gestiona la clasificación de eventos en CalDAV',
    'description_es_ES': 'Gestiona la clasificación de eventos en CalDAV',
    'description_fr_FR': 'Gère la classification des évènements',
    'description_ru_RU': 'Добавление классификации событий в CalDAV',
    'depends' : [
        'ir',
        'calendar',
    ],
    'xml' : [
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
