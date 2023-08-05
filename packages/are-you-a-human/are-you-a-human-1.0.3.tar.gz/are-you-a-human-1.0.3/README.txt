Are You A Human (AYAH) - Python Integration Library
===================================================

SUMMARY
-------

- Documentation and latest version: http://portal.areyouahuman.com/help
- Get an AYAH publisher key: https://portal.areyouahuman.com/
- Discussion group: http://support.areyouahuman.com/

Copyright (c) 2011 AYAH LLC
http://www.areyouahuman.com

BY USING THIS SOFTWARE YOU AGREE TO THE TERMS AND CONDITIONS FOUND AT:
http://portal.areyouahuman.com/termsAndConditions

INSTALLATION
------------

The AYAH Python Integration Library is compatible with Python 2.x and 3.x. (It
was built and tested on versions 2.7.x and 3.2.x.) Python 3.x requires an extra
installation step as described below.

Python 2.x Installation:

1. Download and extract the appropriate source distribution for your OS.
2. Install the package::

      python setup.py install

Python 3.x Installation:

1. Download and extract the appropriate source distribution for your OS.
2. Convert the package to Python 3.x::

      2to3 -wn ./ayah

3. Install the package::

      python3 setup.py install

INTEGRATION
-----------

The AYAH Python Integration Library is compatible with all web application
frameworks.

1. Get your publisher key and scoring key from
   https://portal.areyouahuman.com/.

2. Import the ayah module::

      import ayah

3. Configure the ayah module when your application initializes::

      ayah.configure(<your-publisher-key>, <your-scoring-key>)

4. Display the AYAH HTML on any page that requires a human::

      html = ayah.get_publisher_html()

   Django: you can pass this HTML to the view through the context or simply call
   get_publisher_html() in the template.

5. Allow the alleged human to complete the PlayThru challenge. When they're
   finished, your web page will have a hidden field on it with
   id="session_secret".

6. Use the value of the hidden session secret field to determine if the alleged
   human passed the challenge::

      passed = ayah.score_result(<session-secret>)

   Django: the hidden field will be available in your form object::

      if request.method == 'POST':
          form = LoginForm(request.POST)
          if form.is_valid():
              secret = form.cleaned_data['session_secret']
              passed = ayah.score_result(secret)
              # Redirect...

Congratulations, your application detects humans without requiring CAPTCHA!
