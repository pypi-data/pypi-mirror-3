A way to run Django under PasteDeploy.

An example of the deploy.ini::

    [app:main]
    use = egg:cykooz.djangopaste#django
    settings = project.settings

    [server:main]
    use = egg:Paste#http
    host = localhost
    port = 8000

