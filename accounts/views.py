from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.templatetags.static import static
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Sum
from collections import defaultdict
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from datetime import datetime
from .models import *
from .utils import *
import random



# home_view start

def home_view(request):
    context = {
        "gellaries": Gellary.objects.all(),
        "videos": Video.objects.all(),
        "hero_areas": HeroArea.objects.all(),
    }
    return render(request, "home/layouts/home.html", context)


def about_view(request):
    return render(request, "home/layouts/about.html", {'about_para': AboutParagraph.objects.all(), "about_albums":AboutAlbum.objects.all(), "company_info": CompanyInfo.objects.all()})

def vision(request):
    vision = Vision.objects.all()
    context = {
        "vision" : vision,
    }
    return render(request, "home/layouts/vision.html", context)

def core_values(request):
    core_values = CoreValues.objects.all()
    context = {
        "core_values" : core_values,
    }
    return render(request, "home/layouts/core_values.html", context)

def mission(request):
    mission = Mission.objects.all()
    context = {
        "mission" : mission,
    }
    return render(request, "home/layouts/mission.html", context)



def founder_view(request):
    founders_list = FoundersInfo.objects.all().order_by('id')

    context = {
        'founders_list': founders_list,
        }
    return render(request, "home/layouts/founder.html", context)


def current_executive_commitee(request):
    commitees_list = SispabExecutiveCom.objects.all().order_by('id') 
   
    
    context = {
        'commitees': commitees_list, 
    }
    return render(request, "home/layouts/current_executive_commitee.html", context)

def previous_committee(request):
    commitees_list = PreviousExecutiveCommittee.objects.all().order_by('id')  


    context = {
        'commitees': commitees_list, 
    }
    return render(request, "home/layouts/previous_committee.html", context)
    
    
def membership_rules(request):
    rules_titles = MembershipRules.objects.all()
    context = {
        'rules_titles' : rules_titles,
    }
    return render(request, "home/layouts/membership_rules.html", context)


def process_of_members(request):
    return render(request, "home/layouts/process_of_members.html")

def sisbup_secretariat(request):
    return render(request, "home/layouts/sisbup_secretariat.html")


def benefit_od_member(request):
    return render(request, "home/layouts/benefit_of_member.html")

def advisory_council(request):
    return render(request, "home/layouts/advisory_council.html")

def member_resistation(request):
    return render(request, "home/layouts/member_resistation.html")

def become_a_member(request):
    members = BecomeMember.objects.all().order_by("-id")

    paginator = Paginator(members, 6)   # 6 cards per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "home/layouts/become_a_member.html", {
        "page_obj": page_obj
    })


def sponser_list(request):
    sponsors = Sponsor.objects.all().order_by("-created_at")

    context = {
        "sponsors": sponsors
    }

    return render(request, "home/layouts/sponser_list.html", context)

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Email and password are required")
            return render(request, "home/layouts/login.html")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.user_type == 1:
                login(request, user)
                messages.success(request, "Welcome Admin")
                return redirect("dashboard")

            elif user.user_type == 2:
                login(request, user)
                messages.success(request, "Welcome User")
                return redirect("home")

            else:
                messages.error(request, "Unauthorized user type")
                return render(request, "home/layouts/login.html")

        else:
            messages.error(request, "Invalid email or password")

    return render(request, "home/layouts/login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Logout")
    return redirect('login') 

@login_required
def profile(request):
    aggregator = Aggregator.objects.filter(user=request.user).first()

    context = {
        'aggregator': aggregator,
    }
    
    return render(request, "home/layouts/profile.html", context)


@login_required
def edit_profile(request):
    aggregator = Aggregator.objects.filter(user=request.user).first()

    if not aggregator:
        messages.warning(request, "Profile not found.")
        return redirect('profile')

    if request.method == "POST":
        aggregator.name = request.POST.get("name")
        aggregator.company_name = request.POST.get("company_name")
        aggregator.designation = request.POST.get("designation")
        aggregator.mobile = request.POST.get("mobile")
        aggregator.phone = request.POST.get("phone")
        aggregator.brtc_licence_no = request.POST.get("brtc_licence_no")
        aggregator.tread_licence_no = request.POST.get("tread_licence_no")
        aggregator.n_id = request.POST.get("n_id")
        aggregator.address = request.POST.get("address")

        if request.FILES.get("image"):
            aggregator.image = request.FILES.get("image")

        if request.FILES.get("company_logo"):
            aggregator.company_logo = request.FILES.get("company_logo")

        if request.FILES.get("appoinment_letter"):
            aggregator.appoinment_letter = request.FILES.get("appoinment_letter")

        # Handle CV upload
        if request.FILES.get("cv"):
            aggregator.cv = request.FILES.get("cv")

        aggregator.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    context = {
        "aggregator": aggregator
    }

    return render(request, "home/layouts/edit_profile.html", context)



def registration_view(request):
    # -------- OTP VERIFY / RESEND --------
    if request.method == "POST" and ("otp_code" in request.POST or "resend_otp" in request.POST):
        mobile = normalize_phone(request.POST.get("mobile"))
        reg_data = request.session.get('pending_registration')

        if not reg_data:
            messages.error(request, "Session expired. Please register again.")
            return redirect("registration")

        # -------- RESEND OTP --------
        if "resend_otp" in request.POST:
            # Reset cooldown if mobile changed
            prev_mobile = reg_data.get("mobile")
            if prev_mobile != mobile:
                reg_data['otp_sent_at'] = None
                reg_data['mobile'] = mobile

            otp_last_sent = reg_data.get("otp_sent_at")
            if otp_last_sent:
                elapsed = timezone.now() - timezone.datetime.fromisoformat(otp_last_sent)
                if elapsed.total_seconds() < 60:
                    messages.error(request, "Please wait before requesting a new OTP.")
                    return render(request, "home/layouts/registration.html", {
                        "otp_sent": True,
                        "mobile": mobile
                    })

            sent, otp_msg = send_otp(mobile)
            if sent:
                # Save OTP and timestamp in session
                reg_data['otp'] = otp_msg.replace("-", "")
                reg_data['otp_sent_at'] = timezone.now().isoformat()
                request.session['pending_registration'] = reg_data
                messages.success(request, "OTP resent successfully.")
            else:
                messages.error(request, otp_msg)
            return render(request, "home/layouts/registration.html", {
                "otp_sent": True,
                "mobile": mobile
            })

        # -------- VERIFY OTP --------
        user_otp = request.POST.get("otp_code")
        status, msg = verify_otp(mobile, user_otp)
        if not status:
            messages.error(request, msg)
            return render(request, "home/layouts/registration.html", {
                "otp_sent": True,
                "mobile": mobile
            })

        # -------- SAVE DATA AFTER OTP VERIFIED --------
        TempMember.objects.create(
            company_name=reg_data.get("company_name"),
            person_name=reg_data.get("person_name"),
            designation=reg_data.get("designation"),
            email=reg_data.get("email"),
            mobile=reg_data.get("mobile"),
            phone=reg_data.get("phone"),
            password=reg_data.get("password"),
            brtc_licence_no=reg_data.get("brtc_licence_no"),
            is_aggregator=reg_data.get("is_aggregator"),
            n_id=reg_data.get("n_id"),
            address=reg_data.get("address"),
            cv=reg_data.get("cv_file"),
            appoinment_letter=reg_data.get("app_file"),
            otp=reg_data.get("otp"),
            otp_created_at=timezone.now(),
            status='pending'
        )

        del request.session['pending_registration']
        messages.success(request, "Registration successful! Wait for approval.")
        return redirect("login")

    # -------- INITIAL FORM SUBMISSION --------
    elif request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("registration")

        mobile = normalize_phone(request.POST.get("mobile"))
        email = request.POST.get("email")

        if TempMember.objects.filter(mobile=mobile).exists():
            messages.error(request, "Phone already registered.")
            return redirect("registration")

        # Save uploaded files
        cv = request.FILES.get("cv")
        app_letter = request.FILES.get("appoinment_letter")
        cv_path = default_storage.save(f"cv/{cv.name}", ContentFile(cv.read())) if cv else None
        app_path = default_storage.save(f"letter/{app_letter.name}", ContentFile(app_letter.read())) if app_letter else None

        # -------- SEND OTP (ONLY ON INITIAL FORM SUBMIT) --------
        reg_data = request.session.get('pending_registration', {})

        # Prevent sending multiple OTPs within 60s
        otp_last_sent = reg_data.get("otp_sent_at")
        if otp_last_sent:
            elapsed = timezone.now() - timezone.datetime.fromisoformat(otp_last_sent)
            if elapsed.total_seconds() < 60:
                messages.error(request, "Please wait before requesting a new OTP.")
                return redirect("registration")

        sent, otp_msg = send_otp(mobile)
        if not sent:
            messages.error(request, otp_msg)
            return redirect("registration")

        # Save session with all registration data + OTP
        request.session['pending_registration'] = {
            "company_name": request.POST.get("company_name"),
            "person_name": request.POST.get("person_name"),
            "designation": request.POST.get("designation"),
            "n_id": request.POST.get("n_id"),
            "cv_file": cv_path,
            "app_file": app_path,
            "email": email,
            "mobile": mobile,
            "phone": request.POST.get("phone"),
            "password": make_password(password),
            "brtc_licence_no": request.POST.get("brtc_licence_no", "").strip(),
            "is_aggregator": 'Yes' if request.POST.get("is_aggregator") == 'yes' else 'No',
            "address": request.POST.get("address"),
            "otp": otp_msg.replace("-", ""),
            "otp_created_at": timezone.now().isoformat(),
            "otp_sent_at": timezone.now().isoformat(),
            "otp_sent": True
        }

        messages.success(request, f"OTP sent successfully to {mobile}")
        return render(request, "home/layouts/registration.html", {
            "otp_sent": True,
            "mobile": mobile
        })

    # -------- DEFAULT RENDER --------
    return render(request, "home/layouts/registration.html", {"otp_sent": False})

def search(request):
    member_id = request.GET.get('member_id', '').strip()


    normalized_id = member_id.upper().replace('-', '')

    members = Aggregator.objects.all()
    filtered_members = []
    for member in members:
        code = f'AGM{member.member_id}' if member.user_type == 1 else f'AGU{member.member_id}'
        if normalized_id == code.upper():
            filtered_members.append(member)

    
    paginator = Paginator(filtered_members, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'members': page_obj.object_list,
        'page_obj': page_obj,
        'member_id': member_id,
    }
    return render(request, 'home/layouts/search_result.html', context)


def meeting_calls(request):
    now = timezone.localtime()

    upcoming_list = MeetingTitle.objects.filter(expire_date__gt=now).order_by('expire_date')
    previous_list = MeetingTitle.objects.filter(expire_date__lte=now).order_by('-expire_date')

    upcoming_page_number = request.GET.get('upcoming_page')
    previous_page_number = request.GET.get('previous_page')

    upcoming_paginator = Paginator(upcoming_list, 6)
    previous_paginator = Paginator(previous_list, 6)

    upcoming_meetings = upcoming_paginator.get_page(upcoming_page_number)
    previous_meetings = previous_paginator.get_page(previous_page_number)

    # Get attendee counts and details for each meeting
    for meeting in upcoming_meetings:
        # Count total attendees (sum of no_of_person from all MeetingCall entries)
        meeting_calls = MeetingCall.objects.filter(title=meeting)
        meeting.attendee_count = meeting_calls.aggregate(total=Sum('no_of_person'))['total'] or 0
        
        # Get recent attendees (distinct names)
        recent_calls = meeting_calls.order_by('-created_at')[:3]
        meeting.recent_attendees = []
        for call in recent_calls:
            # Create a simple user-like object for each attendee
            meeting.recent_attendees.append({
                'name': call.name,
                'initials': ''.join([n[0].upper() for n in call.name.split()[:2]]),
                'company': call.company_name
            })
        
        # Calculate total amount collected
        meeting.total_amount = meeting_calls.aggregate(total=Sum('amount'))['total'] or 0
        
        # Count number of bookings
        meeting.total_bookings = meeting_calls.count()
    
    for meeting in previous_meetings:
        # Count total attendees for previous meetings
        meeting_calls = MeetingCall.objects.filter(title=meeting)
        meeting.attendee_count = meeting_calls.aggregate(total=Sum('no_of_person'))['total'] or 0
        
        # Calculate average rating (if you have a rating model, otherwise use random or placeholder)
        # For now, we'll use a placeholder based on attendee count
        if meeting.attendee_count > 0:
            meeting.avg_rating = min(5, round(3.5 + (meeting.attendee_count / 20), 1))
        else:
            meeting.avg_rating = 0
            
        meeting.rating_count = meeting_calls.count()
        
        # Calculate total amount collected
        meeting.total_amount = meeting_calls.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, "home/layouts/meeting_calls.html", {
        'upcoming_meetings': upcoming_meetings,
        'previous_meetings': previous_meetings
    })
User = get_user_model()

def get_aggregator_info(request):
    mobile = request.GET.get('mobile', '').strip()

    mobile = normalize_phone(mobile)

    try:
        # Check Aggregator first
        aggregator = Aggregator.objects.select_related('user').filter(mobile=mobile).first()

        if aggregator:
            return JsonResponse({
                'exists': True,
                'source': 'aggregator',
                'data': {
                    'company_name': aggregator.company_name,
                    'person_name': aggregator.name,
                    'email': aggregator.user.email if aggregator.user else "",
                    'mobile': aggregator.mobile,
                }
            })

        # Check TempMember
        temp = TempMember.objects.filter(mobile=mobile).first()

        if temp:
            return JsonResponse({
                'exists': True,
                'source': 'temp',
                'data': {
                    'company_name': temp.company_name,
                    'person_name': temp.person_name,
                    'email': temp.email,
                    'mobile': temp.mobile,
                }
            })

        return JsonResponse({'exists': False})

    except Exception as e:
        return JsonResponse({'exists': False, 'error': str(e)}, status=500)
    


def meeting_call(request, slug):
    # Get the event/meeting
    last_title = get_object_or_404(MeetingTitle, slug=slug)

    # Create SEO data
    seos = [{
        'meta_title': f"{last_title.title} - Registration | SiSPAB",
        'meta_description': last_title.description[:160] if last_title.description else "Register for this meeting with SiSPAB",
        'meta_keywords': "meeting, registration, sispab, event",
        'meta_url': request.build_absolute_uri(),
        'meta_image': request.build_absolute_uri(last_title.image.url) if last_title.image else request.build_absolute_uri(static('home/images/default-meeting-og.jpg')),
    }]

    # Default form data
    context_data = {
        'company_name': '',
        'name': '',
        'no_of_person': '',
        'mobile': '',
        'email': '',
        'payment_method': '',
        'transection_id': '',
        'payout_number': ''
    }

    if request.method == 'POST':

        for field in context_data:
            context_data[field] = request.POST.get(field, '').strip()

        mobile = context_data['mobile']

        try:
            # persons & price
            no_of_person = int(context_data['no_of_person'] or 1)
            total_price = (last_title.amount or 0) * no_of_person
            screenshot = request.FILES.get('screenshot')

            # save registration
            MeetingCall.objects.create(
                title=last_title,
                company_name=context_data['company_name'],
                name=context_data['name'],
                no_of_person=no_of_person,
                phone=mobile,
                email=context_data['email'],
                payment_method=context_data['payment_method'],
                transection_id=context_data['transection_id'],
                payout_number=context_data['payout_number'],
                screenshot=screenshot,
                amount=total_price
            )

            # SMS message
            message = f"""
Dear {context_data['name']},
Congratulations! Your registration has been successfully completed.

Persons: {no_of_person}
Amount: {total_price} BDT

Thank you for being with us
"""

            if send_sms(mobile, message):
                messages.success(request, "Submitted successfully! SMS sent.")
            else:
                messages.warning(request, "Submitted successfully, but SMS was not sent.")

            return redirect('meeting_call', slug=slug)

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'home/layouts/meeting_call.html', {
        'title': last_title,
        'seos': seos,
        **context_data
    })

def contact_view(request):
    
    return render(request, "home/layouts/contact_page.html")


def blog_view(request):
    blogs = Blog.objects.all().order_by('-date')

    return render(request, "home/layouts/blog_page.html", {
        "blogs": blogs
    })
    
def news_view(request):
    newses = News.objects.all().order_by('-created_at')

    paginator = Paginator(newses, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "home/layouts/news.html", {
        "page_obj": page_obj
    })

def news_detail_view(request, slug):
    news = get_object_or_404(News, slug=slug)
    return render(request, "home/layouts/news_detail.html", { "news": news })


def view_more(request, id):
    blog = get_object_or_404(Blog, id=id)
    return render(request, "home/layouts/view_more_blog_details.html", {"blog": blog})

def complain_view(request):
    aggregators = Aggregator.objects.all()

    if request.method == "POST":
        try:
            aggregator_id = request.POST.get("aggregator")
            aggregator = Aggregator.objects.get(id=aggregator_id) if aggregator_id else None

            complain = ComplainList(
                name=request.POST.get("name"),
                email=request.POST.get("email"),
                phone=request.POST.get("phone"),
                aggregator=aggregator,
                issue=request.POST.get("issue"),
                suggestion=request.POST.get("suggestion"),
            )
            complain.full_clean()
            complain.save()

            messages.success(request, "Your complain has been submitted successfully!")
            return redirect("complain")

        except ValidationError as e:

            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        except Aggregator.DoesNotExist:
            messages.error(request, "Selected aggregator does not exist.")

    return render(request, "home/layouts/complain.html", {"aggregators": aggregators})



def media_view(request):
    all_media = PhotoGallery.objects.all().order_by('year')
    
    media_by_year = {}
    for media in all_media:
        media_by_year.setdefault(media.year, []).append(media)

    return render(request, "home/layouts/media_page.html", {'media_by_year': media_by_year})

def photo_gallery(request, slug):
    album = get_object_or_404(PhotoAlbum, slug=slug)
    all_photos_list = album.photos.all()

    paginator = Paginator(all_photos_list, 9)  # 9 photos per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'album': album,
        'page_obj': page_obj
    }
    return render(request, "home/layouts/photo_gallery.html", context)


def photos(request):
  
    albums_list = PhotoAlbum.objects.all() 

    paginator = Paginator(albums_list, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, "home/layouts/gallery.html", context)




def membership_list(request):
    members = Aggregator.objects.all().order_by('company_name')
    
    # Add pagination - 12 items per page
    paginator = Paginator(members, 12)  # Show 12 members per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "members": members, 
        "page_obj": page_obj, 
    }
    
    return render(request, "home/layouts/membership_lists.html", context)


def member_detail(request, slug):
    member = get_object_or_404(Aggregator, slug=slug)
    context = {
        'member': member
    }
    return render(request, "home/layouts/member_detail.html", context)


def events_view(request):
    events = Events.objects.all()
    events_meetings = Events_Meetings.objects.all()
    context = {
        "events": events,
        "events_meetings": events_meetings
    }
    return render(request, "home/layouts/events.html", context)


def video_gallery(request):
    """
    Display event videos in a paginated gallery.
    """
    # Fetch events with videos
    events = Events.objects.select_related('title').filter(
        url__isnull=False  # Only get events with URLs
    ).exclude(
        url__exact=''  # Exclude empty URLs
    ).order_by('-id')

    # Helper function to generate embed URL
    def generate_embed_url(url):
        if not url:
            return None

        si_param = "FzYOnU1EAQsQ4JFe"

        # If already an embed URL
        if "youtube.com/embed/" in url:
            clean_url = re.sub(r'\?si=.*', '', url)
            return f"{clean_url}?si={si_param}"

        # Extract video ID from normal YouTube URLs
        youtube_regex = (
            r'(?:https?://)?(?:www\.)?'
            r'(?:youtube\.com/watch\?v=|youtu\.be/)'
            r'([A-Za-z0-9_-]{11})'
        )
        match = re.search(youtube_regex, url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}?si={si_param}"

        return url

    # Build video list
    event_videos = []
    for e in events:
        # Get the title string from the ForeignKey
        title_str = e.title.title if e.title else "Untitled Event"
        
        # Generate embed URL
        embed_url = generate_embed_url(e.url)
        
        if embed_url:  # Only add if we have a valid embed URL
            event_videos.append({
                'id': e.id,
                'title': title_str,
                'url': embed_url,
                'created_at': getattr(e, 'created_at', None),
            })

    # Pagination - 6 videos per page
    paginator = Paginator(event_videos, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'events': page_obj.object_list,  # For template compatibility
        'is_paginated': paginator.num_pages > 1,
        'total_videos': len(event_videos),
    }
    
    return render(request, "home/layouts/video_gallery.html", context)

def meetings(request):

    events_meetings = Events_Meetings.objects.all().order_by('title')


    grouped_events = defaultdict(list)
    for event in events_meetings:
        grouped_events[event.title].append(event)


    grouped_events = dict(grouped_events)

    context = {
        "grouped_events": grouped_events,
    }
    return render(request, "home/layouts/meetings.html", context)


def career(request):
    career_list = Career.objects.all().order_by('-id')  # newest first
    paginator = Paginator(career_list, 6)  # show 6 careers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context  = {
        'page_obj': page_obj
    }
    return render(request, "home/layouts/career.html", context)

#home_view end


# admin_view start
@login_required
def dashboard(request):
    return render (request, "admin/pages/dashboard.html")

@login_required
def home_details(request):
    context = {
        "all_company_info" : CompanyInfo.objects.all(),
        "videos": Video.objects.all(), 
        "hero_areas": HeroArea.objects.all(),
    }
    return render (request, 'admin/pages/home_details.html', context)


@login_required
def company_info_input(request, id=None):
    # Get company instance
    if id:
        company = get_object_or_404(CompanyInfo, id=id)
    else:
        company, created = CompanyInfo.objects.get_or_create(id=1)  # <-- FIXED

    if request.method == "POST":
        company_name = request.POST.get("company_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        office_hours = request.POST.get("office_hours")
        day_off_ids = request.POST.getlist("day_off")
        house_no = request.POST.get("house_no")
        block = request.POST.get("block")
        district = request.POST.get("district")
        certificate = request.FILES.get("certificate")
        country = request.POST.get("country")

        # Max 2 days validation
        if len(day_off_ids) > 2:
            messages.error(request, "You can select a maximum of 2 day offs.")
            return redirect(home_details)

        # Update company fields
        company.company_name = company_name
        company.phone = phone
        company.email = email
        company.office_hours = office_hours
        company.house_no = house_no
        company.block = block
        company.district = district
        company.country = country

        if certificate:
            company.certificate = certificate

        company.save()

        # Update many-to-many for day_off
        weekends = Weekend.objects.filter(id__in=day_off_ids)
        company.day_off.set(weekends)

        messages.success(request, "Company information saved successfully!")
        return redirect(home_details)

    # GET request
    weekends = Weekend.objects.all()
    selected_days = list(company.day_off.values_list('id', flat=True))

    return render(request, "admin/pages/company_info_input.html", {
        "company": company,
        "weekends": weekends,
        "selected_days": selected_days,
    })

@login_required
def video_input(request, id):
    video = get_object_or_404(Video, id=id)

    if request.method == "POST":
        video.title = request.POST.get("title")
        video.url = request.POST.get("url")
        video.description = request.POST.get("description")
        video.save()

        messages.success(request, "Video updated successfully!")
        return redirect("video_input", video.id)

    return render(request, "admin/pages/video_input.html", { "video": video })



@login_required
def video_input(request, id=None):
    
    # যদি id থাকে → update mode
    if id:
        video = get_object_or_404(Video, id=id)
    else:
        video = None

    if request.method == "POST":
        title = request.POST.get("title")
        url = request.POST.get("url")
        description = request.POST.get("description")

        if video:  # Update
            video.title = title
            video.url = url
            video.description = description
            video.save()
            messages.success(request, "Video updated successfully!")
        else:  # Create
            Video.objects.create(
                title=title,
                url=url,
                description=description
            )
            messages.success(request, "Video added successfully!")

        return redirect("home_details")

    context = {
        "video": video
    }

    return render(request, "admin/pages/video_input.html", context)

@login_required
def gallry_input(request):
    if request.method == "POST":
        g_name = request.POST.get("gellary_name")
        year = request.POST.get("year")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        image1 = request.FILES.get("image1")
        image2 = request.FILES.get("image2")

        g = Gellary.objects.create(
            gellary_name=g_name,
            year=year,
            description=description,
            image=image,
            image1=image1,
            image2=image2,
        )
        
        messages.success(request, " Photo has been added successfully!")
        return redirect("gallry_input")  
    current_year = datetime.now().year
    return render(request, "admin/pages/gallry_input.html", {'year_list': range(current_year, current_year - 30, -1), })

@login_required
def gallry_update(request, gellary_id):
    gallery = get_object_or_404(Gellary, id=gellary_id)

    if request.method == "POST":
        gallery.gellary_name = request.POST.get("gellary_name")

        year = request.POST.get("year")
        gallery.year = int(year) if year else None

        gallery.description = request.POST.get("description")

        if request.FILES.get("image"):
            gallery.image = request.FILES.get("image")
        if request.FILES.get("image1"):
            gallery.image1 = request.FILES.get("image1")
        if request.FILES.get("image2"):
            gallery.image2 = request.FILES.get("image2")

        gallery.save()
        messages.success(request, "Updated Successfully")
        return redirect("gallry_update", gellary_id=gallery.id)

    current_year = datetime.now().year

    context = {
        "galleries": gallery,
        "year_list": range(current_year, current_year - 30, -1),
    }

    return render(request, "admin/pages/gallry_update.html", context)


@login_required
def gallry_delete(request, gellary_id):
    gallery = get_object_or_404(Gellary, id=gellary_id)
    if request.method == "POST":
        gallery.delete()
        messages.success(request, 'Photo deleted Succesfully')
        return redirect("home_details")
    return render(request, "admin/pages/home_details.html", {"gallery": gallery})


@login_required
def hero_area_input(request, id=None):
    """
    Handles both creating a new HeroArea and updating an existing one.
    If id is provided, it updates; otherwise, it creates a new entry.
    """
    if id:
        # Update existing hero area
        hero_area = get_object_or_404(HeroArea, id=id)
    else:
        # Create new hero area instance
        hero_area = HeroArea()

    if request.method == "POST":
        hero_area.tittle = request.POST.get("tittle")
        hero_area.descriptions = request.POST.get("descriptions")

        # Only update image if a file is uploaded
        if request.FILES.get("image"):
            hero_area.image = request.FILES.get("image")

        hero_area.save()

        if id:
            messages.success(request, "Hero area updated successfully!")
        else:
            messages.success(request, "Hero area created successfully!")

        return redirect("hero_area_input")  # or redirect to a list page

    return render(
        request,
        "admin/pages/hero_area_input.html",
        {"hero": hero_area}
    )

@login_required
def about_details(request):
    context = {
        'about_paragraph': AboutParagraph.objects.all(),
        'about_albums': AboutAlbum.objects.all(),
        'vision': Vision.objects.all(),
        'missions': Mission.objects.all(),
        'core_values': CoreValues.objects.all(),
    }
    return render(request, "admin/pages/about_details.html", context)


@login_required
def update_story(request, id):
    story = get_object_or_404(AboutParagraph, id=id)

    if request.method == "POST":
        title = request.POST.get("title")
        descriptions = request.POST.get("descriptions")

        if not title:
            messages.error(request, "Title cannot be empty")
            return render(request, "admin/pages/update_story.html", {"story": story})

        story.title = title
        story.descriptions = descriptions
        story.save()
        messages.success(request,'Story has been Updated')
        return redirect("update_story", id=story.id)

    return render(request, "admin/pages/update_story.html", {"story": story})

@login_required
def admin_vision(request):
    vision = Vision.objects.all()
    context = {
        'vision' : vision
    }
    return render(request, "admin/pages/vision.html", context)


@login_required
def update_vision(request, id=None):

    if id:
        vision = get_object_or_404(Vision, id=id)
    else:
        vision = None

    if request.method == "POST":
        title = request.POST.get("title")
        descriptions = request.POST.get("descriptions")

        if not title:
            messages.error(request, "Title cannot be empty")
            return render(
                request,
                "admin/pages/vision_input.html",
                {"vision": vision}
            )

        # 🔹 UPDATE
        if vision:
            vision.title = title
            vision.descriptions = descriptions

            if request.FILES.get("image"):
                if vision.image:
                    vision.image.delete(save=False)
                vision.image = request.FILES.get("image")

            vision.save()
            messages.success(request, "Vision updated successfully!")

        # 🔹 CREATE
        else:
            vision = Vision.objects.create(
                title=title,
                descriptions=descriptions,
                image=request.FILES.get("image")
            )
            messages.success(request, "Vision created successfully!")

        return redirect("admin_vision")

    return render(
        request,
        "admin/pages/update_vision.html",
        {"vision": vision}
    )

@login_required
def admin_mission(request):
    mission = Mission.objects.all()
    context = {
        'mission' : mission
    }
    return render(request, "admin/pages/mission.html", context)


@login_required
def mission_input(request, id=None):

    if id:
        mission = get_object_or_404(Mission, id=id)
    else:
        mission = None

    if request.method == "POST":
        title = request.POST.get("title")
        descriptions = request.POST.get("descriptions")

        if not title:
            messages.error(request, "Title cannot be empty")
            return render(
                request,
                "admin/pages/mission_input.html",
                {"mission": mission}
            )

        # 🔹 UPDATE
        if mission:
            mission.title = title
            mission.descriptions = descriptions

            if request.FILES.get("image"):
                if mission.image:
                    mission.image.delete(save=False)
                mission.image = request.FILES.get("image")

            mission.save()
            messages.success(request, "Mission updated successfully!")

        # 🔹 CREATE
        else:
            mission = Mission.objects.create(
                title=title,
                descriptions=descriptions,
                image=request.FILES.get("image")
            )
            messages.success(request, "Mission created successfully!")

        return redirect("admin_mission")

    return render(
        request,
        "admin/pages/update_mission.html",
        {"mission": mission}
    )

@login_required
def admin_core_values(request):
    core_values = CoreValues.objects.all()
    context = {
        'core_values': core_values
    }
    return render(request, "admin/pages/core_values.html", context)

@login_required
def update_core_values(request, id=None):

    if id:
        core_value = get_object_or_404(CoreValues, id=id)
    else:
        core_value = None

    if request.method == "POST":
        title = request.POST.get("title")
        descriptions = request.POST.get("descriptions")

        if not title:
            messages.error(request, "Title cannot be empty")
            return render(
                request,
                "admin/pages/update_core_values.html",
                {"core_value": core_value}
            )

        # 🔹 UPDATE
        if core_value:
            core_value.title = title
            core_value.descriptions = descriptions

            if request.FILES.get("image"):
                core_value.image = request.FILES.get("image")

            core_value.save()
            messages.success(request, "Core Value updated successfully!")

        # 🔹 CREATE
        else:
            core_value = CoreValues.objects.create(
                title=title,
                descriptions=descriptions,
                image=request.FILES.get("image")
            )
            messages.success(request, "Core Value created successfully!")

        return redirect("admin_core_values")

    return render(
        request,
        "admin/pages/update_core_values.html",
        {"core_value": core_value}
    )

@login_required
def album_input(request):
    if request.method == "POST":
        title = request.POST.get("title")
        image_1 = request.FILES.get("image_1")
        image_2 = request.FILES.get("image_2")
        image_3 = request.FILES.get("image_3")
        descriptions = request.POST.get("descriptions")

        g = AboutAlbum.objects.create(
            title=title,
            image_1=image_1,
            image_2=image_2,
            image_3=image_3,
            descriptions=descriptions,
        )
        messages.success(request,'Photo hase been Uploaded')
        return redirect("album_input")  

    return render(request, "admin/pages/album_input.html")

@login_required
def album_update(request, id):
    about_albums = get_object_or_404(AboutAlbum, id=id)

    if request.method == "POST":
        about_albums.title = request.POST.get("title")
        if request.FILES.get("image_1"):
            about_albums.image_1 = request.FILES.get("image_1")
        if request.FILES.get("image_2"):
            about_albums.image_2 = request.FILES.get("image_2")
        if request.FILES.get("image_3"):
            about_albums.image_3 = request.FILES.get("image_3")
        about_albums.descriptions = request.POST.get("descriptions")
        about_albums.save()
        messages.success(request, 'Photo has been Updated')
        return redirect("album_update", id=about_albums.id)

    return render(request, "admin/pages/album_update.html", {"about_albums": about_albums})

@login_required
def album_delete(request, id):
    about_albums = get_object_or_404(AboutAlbum, id=id)
    if request.method == "POST":
        about_albums.delete()
        messages.success(request,'Photo has been Deleted')
        return redirect("about_details")
    return render(request, "admin/pages/about_details.html", {"about_albums": about_albums})




@login_required
def co_sponsers(request):

    if request.method == "POST":
        image_1 = request.FILES.get("image_1")
        image_2 = request.FILES.get("image_2")
        image_3 = request.FILES.get("image_3")
        image_4 = request.FILES.get("image_4")
        image_5 = request.FILES.get("image_5")

        g = Co_sponsers.objects.create(
            image_1=image_1,
            image_2=image_2,
            image_3=image_3,
            image_4=image_4,
            image_5=image_5,
        )
        messages.success(request,'Co-ponser has been created')
        return redirect("co_sponsers")  

    return render(request, "admin/pages/co_sponsers.html")


@login_required
def sponser_update(request, id):
    sponsers = get_object_or_404(Co_sponsers, id=id)

    if request.method == "POST":
        if request.FILES.get("image_1"):
            sponsers.image_1 = request.FILES.get("image_1")

        if request.FILES.get("image_2"):
            sponsers.image_2 = request.FILES.get("image_2")

        if request.FILES.get("image_3"):
            sponsers.image_3 = request.FILES.get("image_3")

        if request.FILES.get("image_4"):
            sponsers.image_4 = request.FILES.get("image_4")

        if request.FILES.get("image_5"):
            sponsers.image_5 = request.FILES.get("image_5")
        sponsers.save()
        messages.success(request,'Co-sposer has been Updated')
        return redirect("sponser_update", id=sponsers.id)

    return render(request, "admin/pages/sponser_update.html", {"sponsers": sponsers})

@login_required
def sponser_delete(request, id):
    sponsers = get_object_or_404(Co_sponsers, id=id)
    if request.method == "POST":
        sponsers.delete()
        messages.success(request,'Co-sponser has been deleted')
        return redirect("about_details")





@login_required
def sispab_founders(request):
    founders_info = FoundersInfo.objects.all()
    context = {
        'founders_info': founders_info
    }
    return render(request, "admin/pages/sispab_founders.html", context)
@login_required
def add_founder(request):
    if request.method == "POST":
        founder_name = request.POST.get("founder_name")
        designation = request.POST.get("designation")
        company = request.POST.get("company")
        founder_image = request.FILES.get("founder_image")
       

        g = FoundersInfo.objects.create(
            founder_name=founder_name,
            designation=designation,
            company=company,
            founder_image=founder_image,
        )
        messages.success(request,'Fouduner has been created')
        return redirect("add_founder")  

    return render(request, "admin/pages/add_founder.html")
@login_required
def founder_update(request, id):
    info = get_object_or_404(FoundersInfo, id=id)

    if request.method == "POST":
        info.founder_name = request.POST.get("founder_name")
        info.designation = request.POST.get("designation")
        info.company = request.POST.get("company")
        if request.FILES.get("founder_image"):
            info.founder_image = request.FILES.get("founder_image")
        info.save()
        messages.success(request,'Founder has been Updated')
        return redirect("founder_update",  id=info.id)

    return render(request, "admin/pages/founder_update.html", {"info": info})

@login_required
def founder_delete(request, id):
    info = get_object_or_404(FoundersInfo, id=id)
    if request.method == "POST":
        info.delete()
        messages.success(request,'Founder has been Deleted')
        return redirect("sispab_founders")
    return render(request, "admin/pages/sispab_founders.html", {"info's": info})




@login_required
def sispab_executive_com(request):
    sispab_executive_com = SispabExecutiveCom.objects.all()
    context = {
        'sispab_executive_com_info': sispab_executive_com
    }
    return render(request, "admin/pages/sispab_executive_com.html", context)

@login_required
def add_sispab_executive_com(request):
    if request.method == "POST":
        name = request.POST.get("name")
        position = request.POST.get("position")
        image = request.FILES.get("image")

        SispabExecutiveCom.objects.create(
            name=name,
            position=position,
            image=image
        )
        messages.success(request, 'Created Successfully')
        return redirect("add_sispab_executive_com")

    return render(request, "admin/pages/add_sispab_executive_com.html")

@login_required
def sispab_executive_com_update(request, id):
    info = get_object_or_404(SispabExecutiveCom, id=id)

    if request.method == "POST":
        info.name = request.POST.get("name")
        info.position = request.POST.get("position")
        if request.FILES.get("image"):
            info.image = request.FILES.get("image")
        info.save()
        messages.success(request,'Updated Successfully')
        return redirect("sispab_executive_com_update",  id=info.id)

    return render(request, "admin/pages/sispab_executive_com_info.html", {"info": info})

@login_required
def sispab_executive_com_delete(request, id):
    info = get_object_or_404(SispabExecutiveCom, id=id)
    if request.method == "POST":
        info.delete()
        messages.success(request,'Deleted Successfully')
        return redirect("sispab_executive_com")
    return render(request, "admin/pages/sispab_executive_com.html", {"info's": info})

@login_required
def previous_executive_committee(request):
    previous_executive_committee = PreviousExecutiveCommittee.objects.all()
    context = {
        'previous_executive_committee_info': previous_executive_committee
    }
    return render(request, "admin/pages/previous_executive_committee.html", context)

@login_required
def add_previous_executive_committee(request):
    if request.method == "POST":
        name = request.POST.get("name")
        position = request.POST.get("position")
        designation = request.POST.get("designation")
        company = request.POST.get("company")
        image = request.FILES.get("image")

        PreviousExecutiveCommittee.objects.create(
            name=name,
            position=position,
            designation=designation,
            company=company,
            image=image
        )
        messages.success(request, 'Created Successfully')
        return redirect("add_previous_executive_committee")

    return render(request, "admin/pages/add_previous_executive_committee.html")

@login_required
def previous_executive_committee_update(request, id):
    info = get_object_or_404(PreviousExecutiveCommittee, id=id)

    if request.method == "POST":
        info.name = request.POST.get("name")
        info.position = request.POST.get("position")
        info.designation = request.POST.get("designation")
        info.company = request.POST.get("company")
        if request.FILES.get("image"):
            info.image = request.FILES.get("image")
        info.save()
        messages.success(request,'Updated Successfully')
        return redirect("previous_executive_committee_update",  id=info.id)

    return render(request, "admin/pages/previous_executive_committee_update.html", {"info": info})

@login_required
def previous_executive_committee_delete(request, id):
    info = get_object_or_404(PreviousExecutiveCommittee, id=id)
    if request.method == "POST":
        info.delete()
        messages.success(request,'Deleted Successfully')
        return redirect("previous_executive_committee")
    return render(request, "admin/pages/previous_executive_committee.html", {"info's": info})

@login_required
def AdminEvents(request):
    events = Events.objects.all()
    meetings = Events_Meetings.objects.all()
    context = {
        'meetings': meetings,
        'events': events
    }
    return render(request, "admin/pages/events.html", context)


@login_required
def admin_video_gallery(request):
    events = Events.objects.all()
    meetings = Events_Meetings.objects.all()
    context = {
        'meetings': meetings,
        'events': events
    }
    return render(request, "admin/pages/admin_video_gallery.html", context)


#video gellary start

@login_required
def upload_video(request):
    if request.method == "POST":
        title_text = request.POST.get("title")
        description_text = request.POST.get("description")
        url = request.POST.get("url")

        event_title = EventTitle.objects.create(
            title=title_text,
            description=description_text
        )

        Events.objects.create(
            title=event_title,
            url=url,
        )

        messages.success(request, "Video uploaded successfully!")
        return redirect("upload_video")

    return render(request, "admin/pages/upload_video.html")




@login_required
def video_update(request, id):
    info = get_object_or_404(Events, id=id)

    if request.method == "POST":
        title_text = request.POST.get("title")
        description_text = request.POST.get("description")

        if info.title:
            info.title.title = title_text
            info.title.description = description_text
            info.title.save()
        else:

            event_title = EventTitle.objects.create(
                title=title_text,
                description=description_text
            )
            info.title = event_title

        info.url = request.POST.get("url")
        info.save()

        messages.success(request, "Updated Successfully")
        return redirect("video_update", id=info.id)

    return render(request, "admin/pages/video_update.html", {"info": info})


@login_required
def video_delete(request, id):
    info = get_object_or_404(Events, id=id)
    if request.method == "POST":
        info.delete()
        messages.success(request,'Deleted Successfully')
        return redirect("AdminEvents")
    return render(request, "admin/pages/events.html")

@login_required
def meeting_create(request):
    if request.method == "POST":
        Events_Meetings.objects.create(
            title=request.POST.get("title"),
            url=request.POST.get("url"),
            description=request.POST.get("description"),
        )
        messages.success(request, "Meeting video uploaded successfully!")
        return redirect("meeting_create")
    
    return render(request, "admin/pages/meeting_create.html", {"action": "Add"})


#vedio_gallary end

@login_required
def meeting_update(request, id):
    meeting = get_object_or_404(Events_Meetings, id=id)

    if request.method == "POST":
        meeting.title = request.POST.get("title")
        meeting.url = request.POST.get("url")
        meeting.description = request.POST.get("description")
        meeting.save()

        messages.success(request, "Meeting video updated successfully!")
        # Use the correct URL name
        return redirect("meeting_video_update", id=meeting.id)

    return render(
        request,
        "admin/pages/meeting_update.html",
        {"meeting": meeting}
    )

@login_required
def meeting_delete(request, id):
    meeting = get_object_or_404(Events_Meetings, id=id)
    if request.method == "POST":
        meeting.delete()
        messages.success(request, "Meeting video deleted successfully!")
        return redirect("AdminEvents")

@login_required
def AdminMedia(request):
    media = PhotoGallery.objects.all()
    context = {
        "media": media
    }
    return render(request, "admin/pages/AminMedia.html", context)

@login_required
def AdminMediaUpload(request):
    if request.method == "POST":
        PhotoGallery.objects.create(
            title=request.POST.get("title"),
            year=request.POST.get("year"),
            description=request.POST.get("description"),
            image=request.FILES.get("image"),
        )
        messages.success(request, "Uploaded successfully")
        
        return redirect("AdminMediaUpload")
    return render(request, "admin/pages/Admin_Media_Upload.html")

@login_required
def AdminMediaUpdate(request, id):
    media = get_object_or_404(PhotoGallery, id=id)

    if request.method == "POST":
        media.title = request.POST.get("title")
        media.year = request.POST.get("year")
        media.description = request.POST.get("description")

        if request.FILES.get("image"):
            media.image = request.FILES.get("image")

        media.save()
        messages.success(request, "Updated successfully")
        return redirect("AdminMediaUpdate", media.id)

    return render(request, "admin/pages/Admin_Media_Update.html", {
        "media": media
    })

@login_required
def AdminMediaDelete(request, id):
    media = get_object_or_404(PhotoGallery, id=id)

    if request.method == "POST":
        media.delete()
        messages.success(request, "Deleted successfully")

    return redirect("AdminMedia")

@login_required
def AdminBlog(request):
    blogs = Blog.objects.all()
    context = {
        "blogs": blogs
    }
    return render(request, "admin/pages/AdminBlog.html", context)

@login_required
def add_blogs(request):
    if request.method == "POST":
        Blog.objects.create(
            title=request.POST.get("title"),
            image=request.FILES.get("image"), 
            date=request.POST.get("date") or None,
            description=request.POST.get("description"),
        )
        messages.success(request, "Blog uploaded successfully")
        return redirect("add_blogs")
    return render(request, "admin/pages/add_blogs.html")

@login_required
def blog_update(request, id):
    blog = get_object_or_404(Blog, id=id)

    if request.method == "POST":
        blog.title = request.POST.get("title")
        blog.date = request.POST.get("date") or None
        blog.description = request.POST.get("description") or None

        if request.FILES.get("image"):
            blog.image = request.FILES.get("image")

        blog.save()
        messages.success(request, "Blog updated successfully")
        return redirect("AdminBlog")

    return render(request, "admin/pages/block_update.html", {"blog": blog})

@login_required
def blog_delete(request, id):
    blog = get_object_or_404(Blog, id=id)
    if request.method == "POST":
        blog.delete()
        messages.success(request, "Blog deleted successfully")
        return redirect("AdminBlog")
    return redirect("AdminBlog")

@login_required
def AdminCampain(request):
    complains = ComplainList.objects.all()
    context = {
        "complains":complains
    }
    return render(request, "admin/pages/complain_list.html", context)

@login_required
def complain_update(request, id):
    complain = get_object_or_404(ComplainList, id=id)

    if request.method == "POST":
        complain.name = request.POST.get("name")
        complain.email = request.POST.get("email")
        complain.phone = request.POST.get("phone") 
        complain.issue = request.POST.get("issue")
        complain.suggetion = request.POST.get("suggetion")

        try:
            complain.full_clean()
            complain.save()

            messages.success(request, "Complain updated successfully")
            return redirect("AdminCampain")

        except ValidationError as e:
            if "phone" in e.message_dict:
                messages.error(request, e.message_dict["phone"][0])
            else:
                messages.error(request, "Invalid data submitted")

    return render(
        request,
        "admin/pages/complain_update.html",
        {"complain": complain}
    )

@login_required
def complain_delete(request, id):
    complain = get_object_or_404(ComplainList, id=id)
    if request.method == "POST":
        complain.delete()
        messages.success(request, "Complain deleted successfully")
        return redirect("AdminCampain")

@login_required
def AdminContact(request):
    contact = Contact_list.objects.all()
    context = {
        'contacts': contact
    }
    return render(request, "admin/pages/contact_list.html", context)


@login_required
def contact_update(request, id):
    contact = get_object_or_404(Contact_list, id=id)

    if request.method == "POST":
        contact.name = request.POST.get("name")
        contact.email = request.POST.get("email")
        contact.address = request.POST.get("address")
        contact.business_name = request.POST.get("business_name")
        contact.message = request.POST.get("message")

        contact.save()
        messages.success(request, "Contact updated successfully!")
        return redirect("AdminContact")

    return render(request, "admin/pages/contact_update.html", {"contact": contact})

@login_required
def contact_delete(request, id):
    contact = get_object_or_404(Contact_list, id=id)

    if request.method == "POST":
        contact.delete()
        messages.success(request, "Contact deleted successfully!")
        return redirect("AdminContact")

    return render(request, "admin/pages/contact_list.html", {"contact": contact})


@login_required
def AdminMembersRules(request):
    membership_rules = MembershipRules.objects.all()
    context = {
         "membership_rules": membership_rules,
    }
    return render(request, "admin/pages/membership_rules.html", context)

@login_required
def AdminMembersRulesAdd(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        rules = request.POST.get("rules")

        MembershipRules.objects.create(
            title=title,
            description=description,
            rules=rules,
        )
        messages.success(request, "Membership rules added successfully!")
        return redirect("AdminMembersRulesAdd")

    return render(request, "admin/pages/add_rules_title_descriptions.html")


@login_required
def AdminMembersRulesUpdate(request, id):
    membership = get_object_or_404(MembershipRules, id=id)

    if request.method == "POST":
        membership.title = request.POST.get("title")
        membership.description = request.POST.get("description")
        membership.rules = request.POST.get("rules")
        membership.save()

        messages.success(
            request,
            "Membership rule updated successfully!"
        )
        return redirect("AdminMembersRulesUpdate", id=id)

    return render(
        request,
        "admin/pages/membership_rules_update.html",
        {"membership": membership}
    )
    

def admin_membership_list(request):
    # Get unverified members (status=1)
    unverified_members = Aggregator.objects.filter(status=1)
    
    # Get verified members (status=2)
    verified_members = Aggregator.objects.filter(status=2)
    # Get temp members (pending registration)
    temp = TempMember.objects.all()
    
    context = {
        'unverified_members': unverified_members,
        'verified_members': verified_members,
        'temp': temp,
        'total_members': verified_members.count(),
        'agm_count': verified_members.filter(is_aggregator="Yes").count(),
        'agu_count': verified_members.filter(is_aggregator="No").count(),
        'verified_count': verified_members.count(),
        'unverified_count': unverified_members.count(),
        # 'exp_count': 0,  # Removed since field doesn't exist
    }
    return render(request, 'admin/pages/admin_membership_list.html', context)

@login_required
def admin_membership_list_details(request, id):
    members = get_object_or_404(Aggregator, id=id)
    comtext = {
        "members" : members
    }
    return render(request, "admin/pages/admin_membership_list_details.html", comtext)

@login_required
def AdminNews(request):
    newses = News.objects.all()
    return render(request, "admin/pages/admin_news.html", {"newses": newses})

@login_required
def AdminAddNews(request):
    if request.method == "POST":
        News.objects.create(
            title=request.POST.get("title"),
            image=request.FILES.get("image"), 
            description=request.POST.get("description"),
        )
        messages.success(request, "News uploaded successfully")
        return redirect("AdminAddNews")
    return render(request, "admin/pages/news_upload.html")



@login_required
def AdminUpdateNews(request, id):
    newses = get_object_or_404(News, id=id)

    if request.method == "POST":
        newses.title = request.POST.get("title")
        
        if request.FILES.get("image"):
            newses.image = request.FILES.get("image")
        
        newses.description = request.POST.get("description")
        
        newses.save()

        messages.success(request, "News updated successfully")
        return redirect("news_update", id=newses.id)

    return render(request, "admin/pages/news_update.html", {
        "newses": newses
    })


@login_required
def AdminNewswDelete(request, id):
    news = get_object_or_404(News, id=id)
    if request.method == "POST":
        news.delete()
        messages.success(request, "News deleted successfully!")
        return redirect("AdminNewa")
    


@login_required
def admin_photo_list(request, id):
    album = get_object_or_404(PhotoAlbum, id = id)
    photos = album.photos.all()
    context = {
        'album': album,
        'photos': photos
    }
    return render(request, 'admin/pages/photo_gallery.html', context)

@login_required
def admin_add_photo(request, id):
    album = get_object_or_404(PhotoAlbum, id=id)
    if request.method == 'POST':
        files = request.FILES.getlist('images')

        if files:
            photos = []
            for file in files:
                photo = Photo.objects.create(album=album, image=file)
                photos.append(photo)

            messages.success(request, "Photos added successfully!")
            return redirect('admin_photo_list', id=album.id)
        else:
            messages.error(request, "Please select at least one image.")

    context = {
        'album': album
    }
    return render(request, 'admin/pages/admin_add_photo.html', context)


@login_required
def admin_update_photo(request, id):
    photo = get_object_or_404(Photo, id=id)
    album = photo.album 

    if request.method == 'POST':
        files = request.FILES.getlist('image')

        if files:
            photo.image = files[0]
            photo.save()

            for file in files[1:]:
                Photo.objects.create(album=photo.album, image=file)

            all_photos = photo.album.photos.all()
            if all_photos:
                photo.album.banner = random.choice(all_photos).image
                photo.album.save()

        messages.success(request, "Photo updated successfully!")
        return redirect('admin_update_photo', id=photo.id)

    return render(request, 'admin/pages/admin_update_photo.html', { 
        'photo': photo, 
        'album': album 
    })

@login_required
def delete_photo(request, id):
    photo = get_object_or_404(Photo, id=id)
    album = photo.album

    if request.method == "POST":
        photo.delete()

        if not album.photos.exists():
            album.delete()
            messages.success(request, "Photo deleted and album removed (no photos left).")
            return redirect("admin_album_list")

        else:
            messages.success(request, "Photo deleted successfully!")
            return redirect("admin_photo_list", album.id)

    


@login_required
def admin_Album_list(request):
    album = PhotoAlbum.objects.all()
    context = {
        'album': album
    }
    return render(request, 'admin/pages/album_list.html', context)

@login_required
def admin_add_album(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')   # ✅ FIXED
        banner = request.FILES.get('banner')

        if title and banner and description:
            PhotoAlbum.objects.create(
                title=title,
                banner=banner,
                description=description
            )
            messages.success(request, "Album created successfully!")
            return redirect('admin_add_album')
        else:
            messages.error(request, "Please enter a title, description and select a banner image.")

    return render(request, 'admin/pages/admin_add_album.html')

@login_required
def admin_update_album(request, id):
    album = get_object_or_404(PhotoAlbum, id=id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')  # ✅ FIXED
        file = request.FILES.get('banner')

        # Update title
        if title and title.strip():
            album.title = title

        # Update description
        if description and description.strip():
            album.description = description

        # Update banner image
        if file:
            album.banner = file

        album.save()  # ✅ Save once only

        messages.success(request, "Album updated successfully!")
        return redirect('admin_update_album', id=album.id)

    return render(request, 'admin/pages/admin_update_album.html', {
        'album': album
    })

@login_required
def delete_album(request, id):
    photo = get_object_or_404(PhotoAlbum, id=id)

    if request.method == "POST":
        photo.delete()
        messages.success(request, "Album deleted successfully!")
        return redirect("admin_Album_list")



@login_required
def admin_career(request):
    careers = Career.objects.all()
    context = {
        'careers': careers
    }
    return render(request, 'admin/pages/admin_career.html', context)


@login_required
def admin_add_career(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        if title and description:
            Career.objects.create(title=title, description=description) 
            messages.success(request, "Career added successfully!")
            return redirect('admin_add_career')
        else:
            messages.error(request, "Please fill all fields.")
            
    return render(request, 'admin/pages/admin_add_career.html')


@login_required
def admin_update_career(request, id):
    career = get_object_or_404(Career, id=id)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        if title and description:
            career.title = title
            career.description = description
            career.save()
            
            messages.success(request, "Career updated successfully!")
            return redirect('admin_career')
        else:
            messages.error(request, "Please fill all fields.")

    return render(request, 'admin/pages/admin_update_career.html', {'career': career})

@login_required
def admin_delete_career(request, id):
    career = get_object_or_404(Career, id=id)
    career.delete()
    messages.success(request, "Career deleted successfully!")
    return redirect('admin_career')




@login_required
def meeting_call_list(request, id):

    title = get_object_or_404(MeetingTitle, id=id)
    calls = MeetingCall.objects.filter(title=title).order_by('-created_at')

    context = {
        'title': title,
        'meeting_calls': calls
    }
    return render(request, "admin/pages/meeting_call_list.html", context)


@login_required
def admin_meeting_call(request):
    titles = MeetingTitle.objects.all()
    context = {
        'titles':titles
    }
    return render(request, "admin/pages/admin_meeting_call.html", context)


@login_required
def meeting_call_add(request):
    if request.method == "POST":
        title_text = request.POST.get('title')
        amount = request.POST.get('amount')
        expire_date = request.POST.get('expire_date')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        # 1. Basic Validation to prevent the "Invalid Date" Crash
        if not title_text:
            messages.error(request, "Title is required!")
            return render(request, "admin/pages/meeting_call_add.html")

        if not expire_date or expire_date == "":
            messages.error(request, "Please select a valid expiry date.")
            return render(request, "admin/pages/meeting_call_add.html")

        # 2. Attempt to create the object
        try:
            MeetingTitle.objects.create(
                title=title_text,
                amount=amount,
                expire_date=expire_date,
                description=description,
                image=image
            )
            messages.success(request, "Meeting call added successfully!")
            return redirect('meeting_call_add')
            
        except Exception as e:
            messages.error(request, f"Error saving meeting: {e}")

    return render(request, "admin/pages/meeting_call_add.html")


@login_required
def meeting_call_update(request, id):
    meeting_title = get_object_or_404(MeetingTitle, id=id)

    if request.method == "POST":
        title_text = request.POST.get('title')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        expire_datetime_str = request.POST.get('expire_date')

        if not title_text:
            messages.error(request, "Title is required!")
            return redirect(request.path)

        meeting_title.title = title_text
        meeting_title.amount = amount
        meeting_title.description = description
        if image:
            meeting_title.image = image
        if expire_datetime_str:
            try:
                expire_datetime = datetime.strptime(expire_datetime_str, "%Y-%m-%d %H:%M")
                meeting_title.expire_date = expire_datetime
            except ValueError:
                messages.error(request, "Invalid date or time format!")
                return redirect(request.path)

        meeting_title.save()
        messages.success(request, "Meeting title updated successfully!")
        return redirect('admin_meeting_call')

    context = {
        'meeting': meeting_title 
    }
    return render(request, "admin/pages/meeting_call_update.html", context)

@login_required
def meeting_call_delete(request, id):
    meeting_call = get_object_or_404(MeetingTitle, id=id)
    meeting_call.delete()
    messages.success(request, "Meeting title deleted successfully!")
    return redirect('admin_meeting_call')



@login_required
def call_update(request, id):
    meeting_call = get_object_or_404(MeetingCall, id=id)

    if request.method == "POST":
        title_id = request.POST.get('title_id')
        company_name = request.POST.get('company_name')
        name = request.POST.get('name')
        no_of_person = request.POST.get('no_of_person')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        payment_method = request.POST.get('payment_method')
        transection_id = request.POST.get('transection_id')

        # Get the title object (ForeignKey)
        if title_id:
            title = get_object_or_404(MeetingTitle, id=title_id)
            meeting_call.title = title

        # Update all other fields
        meeting_call.company_name = company_name
        meeting_call.name = name
        meeting_call.no_of_person = no_of_person
        meeting_call.phone = phone
        meeting_call.email = email
        meeting_call.payment_method = payment_method
        meeting_call.transection_id = transection_id

        meeting_call.save()
        messages.success(request, "Meeting call updated successfully!")

        # ✅ Correct redirect
        return redirect('call_update', id=meeting_call.id)

    # Get all titles for dropdown in template
    titles = MeetingTitle.objects.all().order_by('-id')

    context = {
        'meeting_call': meeting_call,
        'titles': titles
    }
    return render(request, "admin/pages/call_update.html", context)

@login_required
def call_delete(request, id):
    call = get_object_or_404(MeetingCall, id=id)

    call.delete()
    messages.success(request, "Deleted successfully!")

    return redirect('meeting_call_list', call.title.id)




@login_required
def admin_member_registration_list_details(request, id):
    registrations = get_object_or_404(TempMember, id=id)
    context = {
        'registrations': registrations
    }
    return render(request, "admin/pages/admin_member_registration_list_details.html", context)


@login_required
def seo(request):
    seos = Seo.objects.all() 
    context = {
        'seos': seos
    }
    return render(request, "admin/pages/seo.html", context)

@login_required
def edit_seo(request, id):
    seo = get_object_or_404(Seo, id=id)

    if request.method == "POST":
        seo.page_name = request.POST.get("page_name")
        seo.meta_title = request.POST.get("meta_title")
        seo.meta_description = request.POST.get("meta_description")
        seo.meta_keywords = request.POST.get("meta_keywords")
        seo.meta_url = request.POST.get("meta_url")

        # Handle image upload
        if request.FILES.get("meta_image"):
            seo.meta_image = request.FILES.get("meta_image")

        seo.save()
        messages.success(request, "SEO updated successfully")
        return redirect("edit_seo", seo.id)  
    context = {
        "seo": seo
    }
    return render(request, "admin/pages/edit_seo.html", context)


@login_required
def add_seo(request):

    if request.method == "POST":
        page_name = request.POST.get("page_name")

        # Prevent duplicate page
        if Seo.objects.filter(page_name=page_name).exists():
            messages.error(request, "Page already exists")
            return redirect("add_seo")

        seo = Seo(
            page_name=page_name,
            meta_title=request.POST.get("meta_title"),
            meta_description=request.POST.get("meta_description"),
            meta_keywords=request.POST.get("meta_keywords"),
            meta_url=request.POST.get("meta_url"),
            meta_image=request.FILES.get("meta_image")
        )

        seo.save()

        messages.success(request, "SEO added successfully")
        return redirect("add_seo")  

    return render(request, "admin/pages/add_seo.html")

@login_required
def accept(request, id):
    temp_member = get_object_or_404(TempMember, id=id)
    
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                email=temp_member.email,
                user_type=2
            )
            user.password = temp_member.password
            user.save()

            Aggregator.objects.create(
                user=user,
                name=temp_member.person_name,
                company_name=temp_member.company_name,
                designation=temp_member.designation,
                mobile=temp_member.mobile,
                phone=temp_member.phone,
                is_aggregator=temp_member.is_aggregator,
                brtc_licence_no=temp_member.brtc_licence_no,
                appoinment_letter=temp_member.appoinment_letter,
                cv=temp_member.cv,
                address=temp_member.address,
                n_id = temp_member.n_id,
            )

            temp_member.delete()
            
            messages.success(request, f"Member {user.email} has been approved.")

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        
    return redirect('admin_membership_list')

def approve(request, id):
    aggre = get_object_or_404(Aggregator, id=id)
    
    aggre.status = 2 
    aggre.save()     
    
    return redirect('admin_membership_list')

def reject_member(request, id):
    # Get the Aggregator
    aggre = get_object_or_404(Aggregator, id=id)
    aggre.user.delete()
    return redirect('admin_membership_list')

@login_required
def reject(request, id):
    temp_member = get_object_or_404(TempMember, id=id)

    temp_member.delete()
    messages.success(request, "Rejected successfully!")

    return redirect('admin_membership_list')

@login_required
def emergency_services(request):
    # Get all emergency services
    gov_servies = EmergencyServices.objects.all()  # fetch all records

    context = {
        "gov_servies": gov_servies
    }
    return render(request, "admin/pages/emergency_services.html", context)

@login_required
def emergency_services_forms(request, id = None):
    emergency_services = None
    if id:
        emergency_services = get_object_or_404(EmergencyServices, id=id)

    if request.method == "POST":
        title = request.POST.get("title")
        number = request.POST.get("number")
        if emergency_services:
            emergency_services.title = title
            emergency_services.number = number
            emergency_services.save()
            messages.success(request, "Updated Successfully")

        else:
            EmergencyServices.objects.create(
                title=title,
                number=number,
            )
            messages.success(request, "Created Successfully")

        return redirect("emergency_services")

    return render(request, "admin/pages/emergency_services_forms.html", {"emergency_services": emergency_services})

@login_required
def delete_emergency_services(request, id):
    em = get_object_or_404(EmergencyServices, id=id)
    em.delete()
    messages.success(request, f"deleted successfully.")
    return redirect("emergency_services")


@login_required
def government_services(request):
    gov_servies = GovermentServices.objects.all()  # fetch all records

    context = {
        "gov_servies": gov_servies
    }
    return render(request, "admin/pages/government_services.html", context)

@login_required
def government_services_forms(request, id = None):
    government_services = None
    if id:
        government_services = get_object_or_404(GovermentServices, id=id)

    if request.method == "POST":
        title = request.POST.get("title")
        url = request.POST.get("url")
        if government_services:
            government_services.title = title
            government_services.url = url
            government_services.save()
            messages.success(request, "Updated Successfully")

        else:
            GovermentServices.objects.create(
                title=title,
                url=url,
            )
            messages.success(request, "Created Successfully")

        return redirect("government_services")

    return render(request, "admin/pages/government_services_forms.html", {"government_services": government_services})

@login_required
def delete_government_services(request, id):
    em = get_object_or_404(GovermentServices, id=id)
    em.delete()
    messages.success(request, f"deleted successfully.")
    return redirect("government_services")

@login_required
def admin_sponser_list(request):
    sponsors = Sponsor.objects.all()

    context = {
        "sponsors": sponsors,
    }
    return render(request, "admin/pages/admin_sponser_list.html", context)

@login_required
def sponsor_form(request, id=None):

    sponsor = None
    if id:
        sponsor = get_object_or_404(Sponsor, id=id)

    if request.method == "POST":
        sponsor_name = request.POST.get("sponsor_name")
        company_name = request.POST.get("company_name")
        designation = request.POST.get("designation")
        sponsor_email = request.POST.get("sponsor_email")
        sponsor_phone = request.POST.get("sponsor_phone")
        description = request.POST.get("description")
        company_logo = request.FILES.get("company_logo")

        if sponsor:
            sponsor.sponsor_name = sponsor_name
            sponsor.company_name = company_name
            sponsor.designation = designation
            sponsor.sponsor_email = sponsor_email
            sponsor.sponsor_phone = sponsor_phone
            sponsor.description = description

            if company_logo:
                sponsor.company_logo = company_logo

            sponsor.save()
            messages.success(request, "Sponsor Updated Successfully")

        else:
            Sponsor.objects.create(
                sponsor_name=sponsor_name,
                company_name=company_name,
                designation=designation,
                sponsor_email=sponsor_email,
                sponsor_phone=sponsor_phone,
                description=description,
                company_logo=company_logo
            )
            messages.success(request, "Sponsor Created Successfully")

        return redirect("admin_sponser_list")

    return render(request, "admin/pages/sponsor_form.html", {"sponsor": sponsor})



@login_required
def delete_sponsor(request, id):
    sponsor = get_object_or_404(Sponsor, id=id)
    sponsor.delete()
    messages.success(request, f"deleted successfully.")
    return redirect("admin_become_a_member")


@login_required
def admin_become_a_member(request):
    mem = BecomeMember.objects.all()

    context = {
        "mem": mem,
    }
    return render(request, "admin/pages/admin_become_a_member.html", context)

@login_required
def admin_become_a_member_form(request, id=None):

    mem = None
    if id:
        mem = get_object_or_404(BecomeMember, id=id)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        if mem:
            mem.title = title
            mem.description = description
            mem.save()
            messages.success(request, "Updated Successfully")

        else:
            BecomeMember.objects.create(
                title=title,
                description=description,
            )
            messages.success(request, "Created Successfully")

        return redirect("admin_become_a_member")

    return render(request, "admin/pages/admin_become_a_member_form.html", {"mem": mem})



@login_required
def delete_become_a_member(request, id):
    sponsor = get_object_or_404(BecomeMember, id=id)
    sponsor.delete()
    messages.success(request, f"deleted successfully.")
    return redirect("admin_become_a_member")


# admin_view end


#common for all
def contact_submit(request):
   if request.method == "POST":
        Contact_list.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            address=request.POST.get("address"),
            message=request.POST.get("message"),
        )


        messages.success(request, "Thank you! Your message has been sent successfully.")
        return redirect(request.META.get("HTTP_REFERER", "/"))
   
   
   
def check_email(request):
    email = request.GET.get('email', '').strip()

    exists = (
        User.objects.filter(email=email).exists() or
        TempMember.objects.filter(email=email).exists()
    )

    return JsonResponse({'exists': exists})


def check_phone(request):
    mobile = normalize_phone(request.GET.get('mobile', '').strip())

    phone_exists = (
        Aggregator.objects.filter(mobile=mobile).exists() or
        TempMember.objects.filter(mobile=mobile).exists()
    )

    return JsonResponse({'phone_exists': phone_exists})


def check_company(request):
    company = request.GET.get('company_name', '').strip()
    exists = Aggregator.objects.filter(company_name__iexact=company).exists() or TempMember.objects.filter(company_name__iexact=company).exists()
    return JsonResponse({'exists': exists})


#profile