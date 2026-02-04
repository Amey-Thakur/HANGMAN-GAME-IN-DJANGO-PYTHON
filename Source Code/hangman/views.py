import random

from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import render

from hangman import models


def start(request):
    if models.Word.objects.count() == 0:
        charge_db()
    
    # Implementing 40% bias for author names
    if random.random() < 0.4:
        author_list = ['amey', 'mega', 'ameythakur', 'megasatish']
        authors = models.Word.objects.filter(word__in=author_list)
        if authors.exists():
            word = authors.order_by('?').first()
        else:
            word = models.Word.objects.order_by('?').first()
    else:
        word = models.Word.objects.order_by('?').first()

    word_for_friend = models.Word.objects.order_by('?').first()
    
    if not word:
        return render(request, 'index.html', {'error': 'No words found in database.'})
    
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
    """Handle a letter guess from the player."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
    # Get request parameters
    word_id = request.GET.get('wordId')
    letter = request.GET.get('letter', '').strip().lower()
    
    if not word_id or not letter:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    # Get the word
    try:
        word = models.Word.objects.get(id=word_id)
    except models.Word.DoesNotExist:
        return JsonResponse({'error': 'Word not found'}, status=404)
    
    # Get session identifier (use session key or fallback to CSRF token)
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    if not session_id:
        session_id = request.COOKIES.get('csrftoken', 'anonymous')
    
    # Find or create game for this session + word
    game, created = models.Game.objects.get_or_create(
        session=session_id,
        word_id=word_id,
        defaults={'fault': 0, 'letters_known': '', 'win': False}
    )
    
    # Check if already lost
    if game.fault >= 6:
        return JsonResponse({
            'is_lose': True,
            'correct_word': word.word.upper()
        })
    
    # Check if already won
    if game.win:
        word_array = list(word.word)
        return JsonResponse({
            'is_win': True,
            'word_array': word_array
        })
    
    # Process the guess
    target_word = word.word.lower()
    
    if letter in target_word:
        # CORRECT GUESS
        if letter not in game.letters_known.lower():
            game.letters_known += letter
            game.save()
        
        # Build word array for display
        word_array = []
        for char in word.word:
            if char.lower() in game.letters_known.lower():
                word_array.append(char)
            else:
                word_array.append('')
        
        # Check for victory (no empty slots)
        if '' not in word_array:
            game.win = True
            game.save()
            return JsonResponse({
                'is_win': True,
                'word_array': word_array,
                'is_correct': True
            })
        
        # Correct but not won yet
        return JsonResponse({
            'is_win': False,
            'is_correct': True,
            'word_array': word_array,
            'fault_count': game.fault
        })
    else:
        # WRONG GUESS
        game.fault += 1
        game.save()
        
        # Check for loss
        if game.fault >= 6:
            return JsonResponse({
                'is_lose': True,
                'correct_word': word.word.upper()
            })
        
        # Wrong but not lost yet
        return JsonResponse({
            'is_win': False,
            'is_correct': False,
            'fault_count': game.fault
        })

def play_share(request, uuid):
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
    # Implementing 40% bias for author names in secret generation
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
    wordbank_path = settings.BASE_DIR / "static" / "hangman_wordbank.txt"
    try:
        with open(wordbank_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Each line is "word: hint"
                if ':' in line:
                    parts = line.split(':', 1)
                    word_text = parts[0].strip().replace(" ", "").lower()
                    hint_text = parts[1].strip()
                else:
                    word_text = line.strip().replace(" ", "").lower()
                    hint_text = "No hint available."
                
                if not models.Word.objects.filter(word=word_text).exists():
                    models.Word.objects.create(word=word_text, hint=hint_text)
                    
            print(f"Database charged with {models.Word.objects.count()} words.")
            
    except Exception as e:
        print(f"Error charging database: {e}")

def handler404(request, exception):
    return render(request, '404.html', status=404)