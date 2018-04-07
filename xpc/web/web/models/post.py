import pickle
from django.db import models
from web.models.composer import Composer
from web.models.copyright import Copyright
from web.helpers import r
from web.models import Model

class Post(models.Model,Model):
    pid = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=256)
    thumbnail = models.CharField(max_length=512, blank=True, null=True)
    preview = models.CharField(max_length=512, blank=True, null=True)
    video = models.CharField(max_length=512, blank=True, null=True)
    video_format = models.CharField(max_length=32, blank=True, null=True)
    category = models.CharField(max_length=512)
    created_at = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    play_counts = models.IntegerField()
    like_counts = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'posts'

    @property
    def composers(self):
        """取出当前作品的所有作者"""
        # composers = []
        cache_key = 'cr_pid_%s' % self.pid
        composers = [pickle.loads(i) for i in r.lrange(cache_key, 0, -1)]
        # if r.exists(cache_key):

        if not composers:
            cr_list = Copyright.filter(pid=self.pid).all()

            for cr in cr_list:
                composer = Composer.get(cid= cr.cid)
                if composer:
                    composer.role = cr.roles
                    composers.append(composer)
                    r.lpush(cache_key,pickle.dumps(composer))
        return composers

    @property
    def first_composer(self):
        return self.composers[0]
