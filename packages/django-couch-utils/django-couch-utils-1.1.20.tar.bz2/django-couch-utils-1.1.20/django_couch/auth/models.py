from datetime import datetime
from couchdbcurl.client import Document

import random
        


class User(Document):

    def is_active(self):
        """Fake function. Always returns True"""
        return True
    
    def is_authenticated(self):
        """Links to self.is_superuser"""
        return '_id' in self
    
    def get_and_delete_messages(self):
        return None

    def has_perm(self, perm):
        """Permissions system
Django-couch-utils tries to be compliant with basic django permissions system.
So, you must fill user documents with field `permission' which is list of application permission like "module1.permission1".

Example:
{
    username: "...",
    password: "...",
    permissions: ["users.user_edit", "users.user_delete", "files.edit"]
...
}

"""


        return self.is_superuser or perm in self.get_all_permissions()
        
    def has_perms(self, perm_list):
        """See has_perms() docs"""
        
        if self.is_superuser:
            return True
        
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True
    
    
    def has_module_perms(self, module):
        """See has_perms() docs"""
        
        if self.is_superuser:
            return True
        
        modules = set([perm.split('.')[0] for perm in self.get_all_permissions()])
        return module in modules

    def get_all_permissions(self):
        result = []
        
        perms = self.get('permissions', [])
        if self.get('groups'):
            rows = self._db.view('_all_docs', keys=self.groups, include_docs=True).rows
            for row in rows:
                perms.extend(row.doc.permissions)

        return set(perms)
                    
                    
                    
        
    def save(self, *args, **kwargs):
        """Save user object and update ``last_login`` field"""
        
        if hasattr(self, 'backend'):
            backend = self.backend
            del(self.backend)
        else:
            backend = None
            
        if hasattr(self, 'last_login') and type(self.last_login) == datetime:
            from django.conf import settings
            self.last_login = self.last_login.strftime(settings.DATETIME_FMT)

        Document.save(self, *args, **kwargs)

        if backend:
            self.backend = backend

    def set_password(self, raw_password):
        """This is copy-paste from django.contrib.auth.models.User.set_password()"""

        # I need this in runtime, not install time
        from django.contrib.auth.models import get_hexdigest, check_password
        
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)
        

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.

        (c) django.contrib.auth.models.User.check_password()
        """
        
        # I need this in runtime, not install time
        from django.contrib.auth.models import get_hexdigest, check_password
        
        # Backwards-compatibility check. Older passwords won't include the
        # algorithm or salt.
        return check_password(raw_password, self.password)
