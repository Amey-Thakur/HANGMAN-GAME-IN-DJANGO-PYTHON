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
* Central business logic for the Hangman Game. This module manages secret word selection,
* algorithmic game state updates, session-backed security for active matches, and asynchronous
* communication wrappers for the client-side interface.
***************************************************************************************************
'''

import random

from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import render

from hangman import models

def start(request):
    """
    Initializes the primary gameplay environment.
    
    This controller facilitates the bootstrap process for a new game session. It ensures the 
    underlying cryptographic wordbank is populated and selects a secret word for the player.
    
    Algorithmic Bias:
    - Implements a 40% probability bias towards selecting author-specific words ('amey', 'mega', etc.)
      to serve as a personalized easter-egg mechanism within the game's curation logic.
    """
    if models.Word.objects.count() == 0:
        charge_db()
    
    # Selection algorithm with statistical weighting
    if random.random() < 0.4:
        author_list = ['amey', 'mega', 'ameythakur', 'megasatish']
        authors = models.Word.objects.filter(word__in=author_list)
        if authors.exists():
            word = authors.order_by('?').first()
        else:
            word = models.Word.objects.order_by('?').first()
    else:
        word = models.Word.objects.order_by('?').first()

    # Auxiliary word selection for social invitation integration
    word_for_friend = models.Word.objects.order_by('?').first()
    
    if not word:
        return render(request, 'index.html', {'error': 'No words found in database.'})
    
    # Initialize reactive UI state: empty blanks corresponding to word length
    word_array = [""] * len(word.word)
    domain = get_current_site(request)
    
    return render(request, 'index.html', {
        'wordId': word.id, 
        "word": word_array, 
        "fault": 1,
        'wordForFriend': word_for_friend,
        'domain': domain,
        'hint': word.hint
    })

def update_word(request):
    """
    Asynchronous state machine for handling user-initiated letter guesses.
    
    This function operates as the core computational engine for real-time gameplay updates.
    It manages the transition between game states (ongoing, victory, or loss) based on
    character matching against the hidden secret word.
    
    Data Consistency & Security:
    - Utilizes explicit Django session-key filtering (get_or_create) to isolate game instances
      across different clients, preventing state pollution or unauthorized access.
    
    Process Architecture:
    1. Validation: Ensures parameters (wordId, letter) are transmitted via GET.
    2. Retrieval: Locates the active Game instance associated with the session.
    3. Evaluation: Checks the guessed letter against the target string.
    4. Transformation: Updates known letters and fault count synchronously.
    5. Finalization: Returns a serialized JSON response containing the updated UI state.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
    # Parameter Extraction
    word_id = request.GET.get('wordId')
    letter = request.GET.get('letter', '').strip().lower()
    
    if not word_id or not letter:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    # Database Query abstraction for Word instance
    try:
        word = models.Word.objects.get(id=word_id)
    except models.Word.DoesNotExist:
        return JsonResponse({'error': 'Word not found'}, status=404)
    
    # Session lifecycle management for concurrent game isolation
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    if not session_id:
        session_id = request.COOKIES.get('csrftoken', 'anonymous')
    
    # Game state persistence layer
    game, created = models.Game.objects.get_or_create(
        session=session_id,
        word_id=word_id,
        defaults={'fault': 0, 'letters_known': '', 'win': False}
    )
    
    # Termination check: Evaluation of Loss Condition
    if game.fault >= 6:
        return JsonResponse({
            'is_lose': True,
            'correct_word': word.word.upper()
        })
    
    # Termination check: Evaluation of Victory Condition (Pre-emptive)
    if game.win:
        word_array = list(word.word)
        return JsonResponse({
            'is_win': True,
            'word_array': word_array
        })
    
    # Pattern matching against normalized target word
    target_word = word.word.lower()
    
    if letter in target_word:
        # State Update: Successful Match
        if letter not in game.letters_known.lower():
            game.letters_known += letter
            game.save()
        
        # Word Reconstruction for UI presentation
        word_array = []
        for char in word.word:
            if char.lower() in game.letters_known.lower():
                word_array.append(char)
            else:
                word_array.append('')
        
        # Victory Determinism Logic
        if '' not in word_array:
            game.win = True
            game.save()
            return JsonResponse({
                'is_win': True,
                'word_array': word_array,
                'is_correct': True
            })
        
        # Intermediate Success state
        return JsonResponse({
            'is_win': False,
            'is_correct': True,
            'word_array': word_array,
            'fault_count': game.fault
        })
    else:
        # State Update: Incorrect Match (Fault Accumulation)
        game.fault += 1
        game.save()
        
        # Immediate Loss threshold evaluation
        if game.fault >= 6:
            return JsonResponse({
                'is_lose': True,
                'correct_word': word.word.upper()
            })
        
        # Intermediate Failure state
        return JsonResponse({
            'is_win': False,
            'is_correct': False,
            'fault_count': game.fault
        })

def play_share(request, uuid):
    """
    Facilitates 'Share with Friend' functionality via UUID mapping.
    
    Standardized game initialization using a unique universal identifier to allow peer-to-peer
    play matching. Maps the incoming UUID to a specific Word instance in the repository.
    """
    word = models.Word.objects.get(uuid=uuid)
    word_for_friend = models.Word.objects.order_by('?').first()
    
    word_array = [""] * len(word.word)
    domain = get_current_site(request)
    return render(request, 'index.html', {
        'wordId': word.id, 
        "word": word_array, 
        "fault": 1,
        'wordForFriend': word_for_friend,
        'domain': domain,
        'hint': word.hint
    })

def generate_word(request):
    """
    Asynchronous utility for refreshing the 'Invite Friend' word generation.
    
    Returns a JSON payload containing the word and its unique sharing metadata.
    Includes the stylized 40% bias for project author names.
    """
    if random.random() < 0.4:
        author_list = ['amey', 'mega', 'ameythakur', 'megasatish']
        authors = models.Word.objects.filter(word__in=author_list)
        if authors.exists():
            word = authors.order_by('?').first()
        else:
            word = models.Word.objects.order_by('?').first()
    else:
        word = models.Word.objects.order_by('?').first()
    
    domain = get_current_site(request)
    return JsonResponse({
        "word": word.word if word else "", 
        "domain": str(domain), 
        'uuid': str(word.uuid) if word else "",
        'hint': word.hint if word else ""
    })

from django.conf import settings

def charge_db():
    """
    Diagnostic utility for populating the database from flat-file wordbanks.
    
    Parses 'hangman_wordbank.txt' to extract word-hint pairs and ensures persistence
    within the Django ORM layer. Implements sanitization to normalize secret words.
    """
    wordbank_path = settings.BASE_DIR / "static" / "hangman_wordbank.txt"
    try:
        with open(wordbank_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Standardized delimiter parsing (Word:Hint)
                if ':' in line:
                    parts = line.split(':', 1)
                    word_text = parts[0].strip().replace(" ", "").lower()
                    hint_text = parts[1].strip()
                else:
                    word_text = line.strip().replace(" ", "").lower()
                    hint_text = "No hint available."
                
                # Deduplication logic to maintain archive integrity
                if not models.Word.objects.filter(word=word_text).exists():
                    models.Word.objects.create(word=word_text, hint=hint_text)
                    
            print(f"Database charged with {models.Word.objects.count()} words.")
            
    except Exception as e:
        print(f"Error charging database: {e}")

def handler404(request, exception):
    """Custom error handling for 404 Not Found events."""
    return render(request, '404.html', status=404)