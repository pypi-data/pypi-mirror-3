import random
import hashlib
from django.db import models
from django.contrib.auth.models import User

Q = models.Q


class CallbackMapManager(models.Manager):
    def generate_hash(self):
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        random_string = User.objects.make_random_password()
        return hashlib.sha1(salt + random_string).hexdigest()

    def store_callback(self, model_instance):
        hash_id = self.generate_hash()
        while self.get_query_set().filter(hash_id=hash_id).exists():
            hash_id = self.generate_hash()
        return self.create(hash_id=hash_id, content_object=model_instance)

    def all_live_callbacks(self):
        query = Q(is_active=True) & Q(is_error=False)
        return self.get_query_set().filter(query)
