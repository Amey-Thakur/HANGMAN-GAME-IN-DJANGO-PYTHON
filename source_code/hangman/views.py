import random

from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import render

from hangman import models


def start(request):
    for_random_id = []
    for r in models.Word.objects.all():
        for_random_id.append(r.id)
    word_id = random.choice(for_random_id)
    word_id_friend = random.choice(for_random_id)
    word = models.Word.objects.get(id=word_id)
    word_array = []
    for n in range(len(word.word)):
        word_array.append("")
    domain = get_current_site(request)
    return render(request, 'index.html', {'wordId': word_id, "word": word_array, "fault": 1,
                                          'wordForFriend': models.Word.objects.get(id=word_id_friend),
                                          'domain': domain})

def update_word(request):
    word_array = []
    if request.method == 'GET':
        word_id = request.GET.get('wordId')
        fault = request.GET.get('faults')
        letter = request.GET.get('letter')
        game_id = request.GET.get('gameId')
        word = models.Word.objects.get(id=word_id)
        session = ''
        try:
            session = str(request.COOKIES['csrftoken'])
        except:
            pass
        if session != '':
            try:
                session = str(request.META['CSRF_COOKIE'])
            except:
                pass
        game = models.Game.objects.filter(session=session, id=int(game_id))
        if game.count() == 0:
            game = models.Game.objects.create(session=session, word_id=word_id)
        else:
            game = game.first()
            if game.fault >= 6:
                return JsonResponse({'is_lose': True})
        if letter in word.word:
            game.letters_known = game.letters_known + letter
            for v in word.word:
                if v in game.letters_known:
                    word_array.append(v)
                else:
                    word_array.append("")
            if list(word.word) == word_array:
                game.win = True
                game.save()
                return JsonResponse({'is_win': True, 'word_array': word_array})
            game.save()
            return JsonResponse({'game_id': game.id, 'fault_count': 0, 'word_array': word_array, 'is_win': False, 'guessed_letter': letter})
        else:
            game.fault = game.fault + 1
            game.save()
            if game.fault >= 6:
                return JsonResponse({'is_lose': True, 'correct_word': word.word.upper()})
            return JsonResponse({'game_id': game.id, 'fault_count': game.fault + 1, 'is_win': False, 'guessed_letter': letter})

def play_share(request, uuid):
    print(uuid)
    for_random_id = []
    for r in models.Word.objects.all():
        for_random_id.append(r.id)
    word_id_friend = random.choice(for_random_id)
    word = models.Word.objects.get(uuid=uuid)
    word_array = []
    for n in range(len(word.word)):
        word_array.append("")
    domain = get_current_site(request)
    return render(request, 'index.html', {'wordId': word.id, "word": word_array, "fault": 1,
                                          'wordForFriend': models.Word.objects.get(id=word_id_friend),
                                          'domain': domain})

def generate_word(request):
    for_random_id = []
    for r in models.Word.objects.all():
        for_random_id.append(r.id)
    word_id_friend = random.choice(for_random_id)
    word = models.Word.objects.get(id=word_id_friend)
    print(word)
    domain = get_current_site(request)
    return JsonResponse({"word": word.word, "domain": str(domain), 'uuid': str(word.uuid)})

def charge_db():
    file_handle = open("static/hangman_wordbank.txt")
    line = file_handle.readlines()
    array = line[0].split(', ')
    print(array)
    for a in array:
        word = a.replace(" ", "").replace("\n", "")
        exist = models.Word.objects.filter(word=word)
        if exist.count() == 0:
            models.Word.objects.create(word=word)
    for w in models.Word.objects.all():
        print(w.word)