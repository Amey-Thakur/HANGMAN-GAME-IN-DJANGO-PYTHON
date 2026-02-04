'''
***************************************************************************************************
* PROJ NAME: HANGMAN GAME IN DJANGO & PYTHON
* AUTHOR   : Amey Thakur ([GitHub](https://github.com/Amey-Thakur))
* CO-AUTHOR: Mega Satish ([GitHub](https://github.com/msatmod))
* REPO     : [GitHub Repository](https://github.com/Amey-Thakur/HANGMAN-GAME-IN-DJANGO-PYTHON)
* RELEASE  : September 2, 2022
* LICENSE  : MIT License (https://opensource.org/licenses/MIT)
* 
* DESCRIPTION:
* Data Architecture and Schema Definition. This module defines the core entities—Word and Game—
* leveraging the Django ORM to facilitate structured data persistence, relational mapping,
* and unique identification for social sharing.
***************************************************************************************************
'''

import uuid

from django.db import models

class Word(models.Model):
    """
    Entity representation of a secret word and its associated metadata.
    
    Attributes:
    - uuid: A uniquely generated 128-bit identifier used for the 'Share with Friend' logic, 
      ensuring obfuscation of internal database IDs in public URLs.
    - word: The secret target string for the hangman game. Normalization (lowercase) is 
      handled at the ingestion layer (charge_db).
    - hint: A contextual clue assigned to the word to assist player deduction.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=255, verbose_name='Word', unique=True)
    hint = models.CharField(max_length=255, verbose_name='Hint', blank=True, null=True)

    def __str__(self):
        """String representation of the Word entity, primarily for administrative visibility."""
        return str(self.word)

class Game(models.Model):
    """
    Transactional entity tracking the state of an active gameplay session.
    
    This model acts as a snapshot of a player's progress against a specific Word.
    It utilizes a relational link (ForeignKey) to the Word bank and tracks faults,
    discovered letters, and victory status within a session-bound context.
    
    Schema Dynamics:
    - word: Relational mapping to the underlying Word entity (Protected deletion).
    - win: Boolean flag indicating the deterministic victory state.
    - session: A textual identifier (Django session key) used to isolate player states.
    - letters_known: Aggregated string of successfully guessed characters.
    - fault: Numerical counter representing the accumulation of incorrect guesses (0-6).
    """
    word = models.ForeignKey(Word, on_delete=models.PROTECT, verbose_name="Word")
    win = models.BooleanField(verbose_name='Win', default=False)
    session = models.TextField(verbose_name="Session")
    letters_known = models.CharField(verbose_name="Letters Known", default='', max_length=255)
    fault = models.IntegerField(verbose_name="Faults", default=0)

