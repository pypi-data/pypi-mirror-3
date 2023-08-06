Django Prismriver: A light but cool Django admin Theme
=======================================================

Prismriver is another django-admin theme aiming to be good looking while maintaining maximum compatibility with as many django packages as possible, with zero/minimal dependencies.

Aside from that it/will try to be modular with dashboard plugins (not yet implemented) so you can configure it easily the way you prefer.

How it looks
------------

![DjangoCms on Prismriver](https://dl.dropbox.com/u/69084784/prismriver.png)

Requirements
------------

   - Django 1.4
   - 5 mins to configure it.

Installation
------------

   - Put the prismriver directory into your Pythonpath/project folder or install it using pip using:
       - pip install git+https://PolCPP@bitbucket.org/PolCPP/django-prismriver.git
   - In settings.py make sure that:
       - You have staticfiles configured correctly.
       - You look for templates on a '/templates/'  directory.
       - You have the following template context processors.

           TEMPLATE_CONTEXT_PROCESSORS = (
               'django.core.context_processors.request',
               'django.contrib.auth.context_processors.auth',
           )

       - On INSTALLED_APPS make sure you add the 'prismriver' app before django.contrib.admin. For example like this:

           INSTALLED_APPS = (
               'prismriver',
               'django.contrib.auth',
               'django.contrib.contenttypes',
               'django.contrib.sessions',
               'django.contrib.sites',
               'django.contrib.messages',
               'django.contrib.staticfiles',
               'django.contrib.admin',
           )

       - Run your server and it works!
       - Now there are some extended settings if you want to customize the sidebar.
          - **CUSTOM_MENU**: Allows you to enable the custom menu. By default this is false.
          - **SIDEBAR_APP_MENU**: When the previous option is true, it allows you to create "Folders/Menus" contontaining various models. For example imagine you want to unify the auth and sites apps in one menu with all it's options inside. Well, we do the following:

             SIDEBAR_APP_MENU = [
                    {"name": "Users and Settings",
                     "items": ["auth", "prismriver", "sites"],
                     "icon": "users.png",
                     "big_icon": "users_big.png",
                     "description": "Manage everything about the users here",
                     },
             ]

          - **SIDEBAR_LAST_ACTIONS**: Shows the last actions widget thing. By default this is true          

          - **DEFAULT_LABELS** If don't want custom menu but you want to use different labels/icons for your applications you can configure them as following:

              DEFAULT_LABELS = {

              "auth/": ["Users and Groups", "users.png", "users_big.png","Manage the application users or groups permissions"], 
              
              "sites/": ["Site management", "web.png", "web_big.png", "Manages the sites application"]}

          *The "web_big.png" field is not used, it will be removed on the next updates (old version stuff)*

          - *For more details you can see prismriver/settings.py*