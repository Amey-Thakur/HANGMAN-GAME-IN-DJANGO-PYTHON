import random

from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import render

from hangMansApp import models


def Start(request):
    forRandomId = []
    for r in models.Word.objects.all():
        forRandomId.append(r.id)
    wordId = random.choice(forRandomId)
    wordIdFriend = random.choice(forRandomId)
    word = models.Word.objects.get(id=wordId)
    wordArray = []
    for n in range(len(word.word)):
        wordArray.append("")
    domain = get_current_site(request)
    return render(request, 'index.html', {'wordId': wordId, "word": wordArray, "fault": 1,
                                          'wordForFriend': models.Word.objects.get(id=wordIdFriend),
                                          'domain': domain})

def updateWord(request):
    wordArray = []
    if request.method == 'GET':
        wordId = request.GET.get('wordId')
        fault = request.GET.get('faults')
        letter = request.GET.get('letter')
        gameId = request.GET.get('gameId')
        word = models.Word.objects.get(id=wordId)
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
        game = models.Game.objects.filter(session=session, id=int(gameId))
        if game.count() == 0:
            game = models.Game.objects.create(session=session, word_id=wordId)
        else:
            game = game.first()
            if game.fault >= 6:
                return JsonResponse({'lose': True})
        if letter in word.word:
            game.letterKnows = game.letterKnows + letter
            for v in word.word:
                if v in game.letterKnows:
                    wordArray.append(v)
                else:
                    wordArray.append("")
            if list(word.word) == wordArray:
                game.win = True
                game.save()
                return JsonResponse({'win': True, 'wordArray': wordArray})
            game.save()
            return JsonResponse({'gameId': game.id, 'fault': 0, 'wordArray': wordArray, 'win': False, 'letter': letter})
        else:
            game.fault = game.fault + 1
            game.save()
            if game.fault >= 6:
                return JsonResponse({'lose': True, 'word': word.word.upper()})
            return JsonResponse({'gameId': game.id, 'fault': game.fault + 1, 'win': False, 'letter': letter})

def playShare(request, uui):
    print(uui)
    forRandomId = []
    for r in models.Word.objects.all():
        forRandomId.append(r.id)
    wordIdFriend = random.choice(forRandomId)
    word = models.Word.objects.get(uui=uui)
    wordArray = []
    for n in range(len(word.word)):
        wordArray.append("")
    domain = get_current_site(request)
    return render(request, 'index.html', {'wordId': word.id, "word": wordArray, "fault": 1,
                                          'wordForFriend': models.Word.objects.get(id=wordIdFriend),
                                          'domain': domain})

def generateWord(request):
    forRandomId = []
    for r in models.Word.objects.all():
        forRandomId.append(r.id)
    wordIdFriend = random.choice(forRandomId)
    word = models.Word.objects.get(id=wordIdFriend)
    print(word)
    domain = get_current_site(request)
    return JsonResponse({"word": word.word, "domain": str(domain), 'uuid': str(word.uui)})

def chargeDB():
    fich = open("static/Hangman_wordbank.txt")
    line = fich.readlines()
    array = line[0].split(', ')
    print(array)
    for a in array:
        word = a.replace(" ", "").replace("\n", "")
        exist = models.Word.objects.filter(word=word)
        if exist.count() == 0:
            models.Word.objects.create(word=word)
    for w in models.Word.objects.all():
        print(w.word)