"""
Installation

# easy_install django-admin-skel

Using

0. settings.INSTALLED_APPS = (
    ...
    'admin_skel'
    ...
)

1. Your admin templates must extends admin_skel/index.html

{% extends "admin_skel/index.html" %}

2. You must define blocks "header", "content", "footer", "title" in your templates

3. You can define block "scripts" to load add scripts into <header> tag

4. You must provide menu into template in such format:
   menu = [
        {
            'title': _(u'Top menu 1'),
            'url': reverse('some url'),
        },
        {
            'title': _(u'Top menu 2'),
            'url': reverse('some another url'),
        },
        {
            'title': _(u'Top menu 3 with subitems'),
            'submenu': [
              {
               'title': _(u'Submenu 1'),
               'url': reverse('submenu url'),
               ...
            
            ]
        },


   
   ]

This may be done by context-processor

#settings.py

TEMPLATE_CONTEXT_PROCESSORS = (
   ...
 	'main.context_processors.menu',
   ...
)


#main.context_processors

def menu(request):
    
    menu = [
        {
            'title': _(u'Devices'),
            'url': reverse('admin:devices'),
        },
        {
            'title': _(u'Developers'),
            'url': reverse('admin:developers'),
        },
        {
            'title': _(u'Users'),
            'url': reverse('admin:users'),
        }
    ]

    selected = None
    opened = None
    if request.path != '/':
        # select and open direct match
        for item in menu:
            if 'submenu' in item:
                for subitem in item['submenu']:
                    if subitem['url'] == request.path:
                        subitem['selected'] = True
                        item['opened'] = True
                        selected = subitem
                        opened = item
                        break
            else:
                if item['url'] == request.path:
                    item['selected'] = True
                    selected = item
                    break

        # open almost-the-same items
        if not opened:
            for item in menu:
                if 'submenu' in item:
                    for subitem in item['submenu']:
                        if request.path.startswith(subitem['url']):
                            item['opened'] = True
                            break
    
    return {'menu': menu}


5. You may override menu rendered with your own by defining block "menu"

"""
