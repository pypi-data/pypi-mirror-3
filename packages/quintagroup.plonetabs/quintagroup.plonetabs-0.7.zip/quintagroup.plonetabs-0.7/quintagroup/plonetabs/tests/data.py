PORTAL_ACTIONS = (
    ('portal_tabs', {
        'children': (
            ('home', {
                'title': 'Our home',
                'description': 'The most important place',
                'i18n_domain': 'quintagroup.plonetabs',
                'url_expr': 'string:${globals_view/navigationRootUrl}',
                'icon_expr': '',
                'available_expr': '',
                'permissions': ('View',),
                'visible': True,
                'type': 'action',
            }),
            ('quintagroup', {
                'title': 'Quintagroup',
                'description': 'Quintagroup.com',
                'i18n_domain': 'quintagroup.plonetabs',
                'url_expr': 'string:http://quintagroup.com',
                'icon_expr': '',
                'available_expr': '',
                'permissions': ('View',),
                'visible': True,
                'type': 'action',
            }),
        ),
        'type': 'category',
    }),
    ('new_category', {
        'children': (
            ('one', {
                'title': 'First action',
                'description': 'From the very beginning',
                'i18n_domain': 'quintagroup.plonetabs',
                'url_expr': 'string:${globals_view/navigationRootUrl}',
                'icon_expr': '',
                'available_expr': '',
                'permissions': ('View',),
                'visible': True,
                'type': 'action',
            }),
        ),
        'type': 'category',
    }),
)

PORTAL_CONTENT = (
    ('folder1', {
        'Title': 'Folder #1',
        'Description': 'Folder #1 description',
        'children': (),
        'type': 'Folder',
    }),
    ('document1', {
        'Title': 'Document #1',
        'Description': 'Document #1 description',
        'text': 'Document #1 body text',
        'type': 'Document',
    }),
)
