from .models import *
from django.urls import reverse

def company_info(request):
    return {
        'all_company_info': Company_info.objects.all(),
        'co_sponsers': Co_sponsers.objects.all()
    }

def global_search_data(request):
    LIMIT = 50
    search_items = []

    for f in FoundersInfo.objects.all()[:LIMIT]:
        search_items.append((f.founder_name, reverse('founder')))

    for b in Blog.objects.all()[:LIMIT]:
        search_items.append((b.title, reverse('blog')))

    for m in PhotoGallery.objects.all()[:LIMIT]:
        search_items.append((m.title, reverse('media')))

    for e in Events.objects.all()[:LIMIT]:
        search_items.append((e.title, reverse('events')))

    for em in Events_Meetings.objects.all()[:LIMIT]:
        search_items.append((em.title, reverse('events')))


    for c in Company_info.objects.all()[:LIMIT]:
        search_items.append((c.company_name, reverse('about')))


    for v in Video.objects.all()[:LIMIT]:
        search_items.append((v.title, reverse('home')))


    for ex in SispabExecutiveCom.objects.all()[:LIMIT]:

        search_items.append((ex.name, reverse('current_executive_commitee')))

    for pe in PreviousExecutiveCommittee.objects.all()[:LIMIT]:

        search_items.append((pe.name, reverse('previous_committee')))

    return {"global_search_items": search_items}