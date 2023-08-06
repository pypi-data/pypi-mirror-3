Google Federated Auth for Flask
===============================

Require an account from a given Google Apps domain for your Flask apps.

Great for internal apps on public-facing servers.


Usage
-----

Setup is super simple::

    from flask import Flask
    from flask_googlefed import GoogleAuth

    app = Flask(__name__)
    app.config['GOOGLE_DOMAIN'] = 'heroku.com'
    app.config['SECRET_KEY'] = 'ssssshhhhh'

    auth = GoogleAuth(app)

    @app.route('/')
    @auth.required
    def secret():
        return 'ssssshhhhh'


Install
-------

Installation ::

    $ pip install flask-googlefed


TODO
----

Be forewarned, there's work to be done:

- ``g.user`` is always ``None``
- More generic Google auth would be nice.
