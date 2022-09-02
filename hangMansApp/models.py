import uuid

from django.db import models

class Word(models.Model):
    uui = models.UUIDField(default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=255, verbose_name='Word', unique=True)

    def __str__(self):
        return str(self.word)

class Game(models.Model):
    word = models.ForeignKey(Word, on_delete=models.PROTECT, verbose_name="Word")
    win = models.BooleanField(verbose_name='Win', default=False)
    session = models.TextField(verbose_name="Session")
    letterKnows = models.CharField(verbose_name="Letter Knows", default='', max_length=255)
    fault = models.IntegerField(verbose_name="Faults", default=0)
