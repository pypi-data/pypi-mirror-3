
import django
if django.VERSION > (1, 4):
    from django.contrib.auth.hashers import check_password, make_password
else:
    from django.contrib.auth.models import check_password
    
    import hashlib
    import random

    def make_password(password, salt=None):
        """Pre-django 1.4 hashing scheme"""

        if not salt:
            salt = hashlib.sha1(str(random.random()) + str(random.random())).hexdigest()[:5]
            
        hsh = hashlib.sha1(salt, password)
        return 'sha1$%s$%s' % (salt, hsh)
    

