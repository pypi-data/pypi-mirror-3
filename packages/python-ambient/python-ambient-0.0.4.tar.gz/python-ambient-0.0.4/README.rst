Python Ambient
==============

Python Ambient Mobile integration library.

Sending Messages
----------------

Example::

    import ambient
    sms = ambient.AmbientSMS(api_key='<your_api_key_here>', password='<your_password_here>')
    sms.sendmsg('<message_content_here>', ['44233562736', '27782343748', '<more_numbers_here>'])

