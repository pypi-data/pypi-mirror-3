Manual
++++++

This package provides handy middleware and Apache configs for working with
mod_wsgi.

.. automodule:: apachemiddleware 
   :members:
   :undoc-members:

Here's a handy Apache config for having Apache serve static file whilst
allowing mod_wsgi to serve all other requests:

::

    # Set up logging for mod_rewrite
    RewriteLog "/var/www/staging/log/apache.rewrite.log"
    RewriteLogLevel 10
    RewriteEngine On
    # Disallow direct access to /wsgi
    RewriteRule ^/wsgi/(.*)$ /$1 [R=301,QSA]
    # Apache shouldn't handle .py files
    RewriteCond %{REQUEST_URI} ^(.*)\.py$
    RewriteRule ^/(.*)$ /wsgi/$1 [PT,L,QSA]
    # Apache shouldn't pass through files ro the WSGI script
    RewriteCond %{DOCUMENT_ROOT}%{REQUEST_FILENAME} !-f
    RewriteRule ^/(.*)$ /wsgi//$1 [PT,L,QSA]
    # If we still haven't returned a response or passed the request to the WSGI app, let Apache handle it, serving the static file
    
    DirectorySlash Off
    
    DocumentRoot /var/www/staging/site_root 
    
    <Directory /var/www/staging/site_root>
        Options FollowSymlinks
        DirectoryIndex index.html
        AllowOverride None
        Order allow,deny
        Allow from all
    </Directory>
    
    # Dynamic Files
    WSGIScriptAlias /wsgi /var/www/staging/deploy.py


I usually write my ``deploy.py`` files like this, with ``/home/staging/env``
being a virtual environment.

::

    #!/home/staging/env/bin/python
    
    import os
    import site
    site.addsitedir('/home/staging/env/lib/python2.6/site-packages')
    # Avoid ``[Errno 13] Permission denied: '/var/www/.python-eggs'`` messages
    os.environ['PYTHON_EGG_CACHE'] = '/tmp'
    # Set the locale for the application
    import locale
    locale.setlocale(locale.LC_ALL, ('en_GB', 'UTF-8'))
    # Now start ordinary code
    application = yourwsigapp()

