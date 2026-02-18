from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from datetime import datetime
from collections import defaultdict
from django.db import transaction
from django.http import JsonResponse
from .models import *
import random, time, hashlib
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from .utils import send_sms
import random
import requests





# home_view start

def home_view(request):
    context = {
        "gellaries": Gellary.objects.all(),
        "videos": Video.objects.all(),
        "hero_areas": HeroArea.objects.all(),
    }
    return render(request, "home/layouts/home.html", context)


def about_view(request):
    return render(request, "home/layouts/about.html", {'about_para': AboutParagraph.objects.all(), "about_albums":AboutAlbum.objects.all(), "company_info": Company_info.objects.all()})

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
    founders = FoundersInfo.objects.all()
    context = {
        'founders' : founders
    }
    return render(request, "home/layouts/founder.html", context)

def current_executive_commitee(request):
    commitees = SispabExecutiveCom.objects.all()
    context = {
        'commitees': commitees
    }
    return render(request, "home/layouts/current_executive_commitee.html", context)

def previous_committee(request):
    commitees = PreviousExecutiveCommittee.objects.all()
    context = {
        'commitees' : commitees
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

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Email and password are required")
            return render(request, "home/layouts/login.html")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if user.user_type == 1:
                messages.success(request, "Welcome to Sispub")
                return redirect("dashboard")
            else:
                messages.success(request, "Login Succesfully")                    
                return redirect("home")

        else:
            messages.error(request, "Invalid email or password")

    return render(request, "home/layouts/login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Logout")
    return redirect('login')

# ===================== SMS Gateway Config =====================
SMS_API_URL = "http://sms.iglweb.com/api/v1/send"
SMS_API_KEY = "4451764741797151764741797"
SMS_SENDER_ID = "01844532630"

# ===================== Phone Normalization =====================
def normalize_phone(phone):
    phone = phone.strip()
    if phone.startswith("0"):
        return "880" + phone[1:]  # IGL expects 88017XXXXXXX format
    elif phone.startswith("880"):
        return phone
    elif phone.startswith("+880"):
        return phone[1:]
    else:
        return phone

# ===================== Send SMS =====================
def send_sms(phone_1, message):
    """
    Send SMS using IGL SMS API
    """
    try:
        phone = normalize_phone(phone_1)
        payload = {
            "api_key": SMS_API_KEY,
            "contacts": phone,        # Correct parameter
            "senderid": SMS_SENDER_ID,
            "msg": message            # Correct parameter
        }
        response = requests.post(SMS_API_URL, data=payload, timeout=10)
        resp_json = response.json()

        if response.status_code == 200 and resp_json.get("code") == "445000":
            print(f"OTP sent successfully to {phone}: {message}")
            return True
        else:
            print(f"Failed to send SMS. API Response: {resp_json}")
            return False
    except Exception as e:
        print(f"Exception sending SMS: {e}")
        return False

# ===================== OTP Hash =====================
def hash_otp(otp):
    return hashlib.sha256(otp.encode()).hexdigest()


def registration_view(request):

    # ----- OTP Verification -----
    if request.method == "POST" and "otp_code" in request.POST:
        user_otp = request.POST.get("otp_code")
        session_otp = request.session.get("otp")
        otp_time = request.session.get("otp_time")
        reg_data = request.session.get("reg_data")

        if not reg_data:
            messages.error(request, "Session expired. Try again.")
            return redirect("registration")

        if time.time() - otp_time > 300:
            messages.error(request, "OTP expired.")
            return redirect("registration")

        if hash_otp(user_otp) != session_otp:
            attempts = request.session.get("otp_attempts", 0) + 1
            request.session["otp_attempts"] = attempts
            if attempts >= 5:
                messages.error(request, "Too many attempts.")
                return redirect("registration")
            messages.error(request, "Invalid OTP.")
            return render(request, "home/layouts/resistation.html", {"otp_sent": True, "phone": reg_data["phone"]})

        # Create user and profile
        try:
            with transaction.atomic():
                # Logic: If it's an aggregator, user_type is 3, else 2
                u_type = 3 if reg_data.get("is_aggregator_flag") else 2
                
                user = User.objects.create_user(
                    email=reg_data["email"],
                    password=reg_data["password"],
                    user_type=u_type
                )

                Aggregator.objects.create(
                    user=user,
                    name=reg_data["name"],
                    company_name=reg_data["company_name"],
                    designation=reg_data["designation"],
                    phone=reg_data["phone"],
                    brtc_licence_no=reg_data.get("brtc_licence_no", ""),
                    address=reg_data["address"]
                )

            request.session.flush()
            messages.success(request, "Account created successfully!")
            return redirect("registration")

        except Exception as e:
            messages.error(request, str(e))
            return redirect("registration")

    # ----- Registration Form Submission (Phase 1: Send OTP) -----
    elif request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("registration")

        # Check hidden input value "1" from HTML
        is_aggregator = request.POST.get("is_aggregator") == "1"
        brtc_no = request.POST.get("brtc_licence_no", "").strip()

        # Mandatory check for Type 3 (Aggregator)
        if is_aggregator and not brtc_no:
            messages.error(request, "BRTC License is mandatory for Aggregators.")
            return redirect("registration")

        reg_data = {
            "name": request.POST.get("name"),
            "company_name": request.POST.get("company_name"),
            "designation": request.POST.get("designation"),
            "email": request.POST.get("email"),
            "password": password,
            "phone": request.POST.get("phone"),
            "brtc_licence_no": brtc_no if is_aggregator else "",
            "is_aggregator_flag": is_aggregator, # Store the choice for user_type logic
            "address": request.POST.get("address"),
        }

        if User.objects.filter(email=reg_data["email"]).exists():
            messages.error(request, "Email already exists")
            return redirect("registration")

        if Aggregator.objects.filter(phone=reg_data["phone"]).exists():
            messages.error(request, "Phone number already exists")
            return redirect("registration")

        # OTP Logic
        otp = str(random.randint(100000, 999999))
        request.session["reg_data"] = reg_data
        request.session["otp"] = hash_otp(otp)
        request.session["otp_time"] = time.time()
        request.session["otp_attempts"] = 0

        sms_sent = send_sms(reg_data["phone"], f"Your OTP is {otp}")
        if not sms_sent:
            messages.error(request, "Failed to send OTP. Please try again.")
            return redirect("registration")

        return render(request, "home/layouts/resistation.html", {"otp_sent": True, "phone": reg_data["phone"]})

    return render(request, "home/layouts/resistation.html", {"otp_sent": False})

# ===================== Resend OTP =====================
@csrf_exempt
def resend_otp(request):
    if request.method == "POST":
        reg_data = request.session.get("reg_data")
        if not reg_data:
            return JsonResponse({"status": "expired"})

        otp = str(random.randint(100000, 999999))
        request.session["otp"] = hash_otp(otp)
        request.session["otp_time"] = time.time()

        sms_sent = send_sms(reg_data["phone"], f"Your OTP is {otp}")
        if not sms_sent:
            return JsonResponse({"status": "failed"})

        return JsonResponse({"status": "ok"})
    





def meeting_calls(request):
    meeting_titles = MeetingTitle.objects.all()
    return render(request, "home/layouts/meeting_calls.html", {"meeting_titles": meeting_titles})


User = get_user_model()

def get_aggregator_info(request):
    phone = request.GET.get('phone', '').strip()

    if phone.startswith("+880"):
        phone = phone[3:]
    elif phone.startswith("880"):
        phone = phone[2:]

    try:
        aggregator = Aggregator.objects.select_related('user').filter(phone=phone).first()

        if aggregator:
            data = {
                'company_name': aggregator.company_name,
                'name': aggregator.name,
                'no_of_person': getattr(aggregator, 'no_of_person', 1),
                'email': aggregator.user.email if aggregator.user else "",
            }
            return JsonResponse({'exists': True, 'data': data})
        
        return JsonResponse({'exists': False, 'data': {}})

    except Exception as e:
        return JsonResponse({'exists': False, 'error': str(e)}, status=500)
    

def meeting_call(request, id):
    last_title = get_object_or_404(MeetingTitle, id=id)

    # Initialize empty form data
    context_data = {
        'company_name': '', 'name': '', 'no_of_person': '',
        'phone': '', 'email': '', 'payment_method': '', 'transection_id': '',
    }

    if request.method == 'POST':
        # Update context with submitted data to repopulate on error
        for field in context_data:
            context_data[field] = request.POST.get(field, '').strip()

        # 1. Server-side Membership Check (Security)
        phone = context_data['phone']
        if not Aggregator.objects.filter(phone__icontains=phone[-10:]).exists():
            messages.error(request, "Registration failed: Phone number not found in member list.")
            return render(request, 'home/layouts/meeting_call.html', {'title': last_title, **context_data})

        # 2. Save logic
        try:
            no_of_person = int(context_data['no_of_person'])
            total_price = (last_title.amount or 0) * no_of_person

            MeetingCall.objects.create(
                title=last_title,
                company_name=context_data['company_name'],
                name=context_data['name'],
                no_of_person=no_of_person,
                phone=context_data['phone'],
                email=context_data['email'],
                payment_method=context_data['payment_method'],
                transection_id=context_data['transection_id'],
                amount=total_price
            )
            messages.success(request, "Submitted successfully!")
            return redirect('meeting_call', id=last_title.id)
        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'home/layouts/meeting_call.html', {'title': last_title, **context_data})

def contact_view(request):
    
    return render(request, "home/layouts/contact_page.html")


def blog_view(request):
    blogs = Blog.objects.all().order_by('-date')

    return render(request, "home/layouts/blog_page.html", {
        "blogs": blogs
    })
    
def news_view(request):
    newses = News.objects.all().order_by('-date')
    return render(request, "home/layouts/news.html", { "newses": newses })

def news_detail_view(request, id):
    news = get_object_or_404(News, id=id)
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

def photo_gallery(request, id):
    album = get_object_or_404(PhotoAlbum, id=id)
    all_photos = album.photos.all()
    return render(request, "home/layouts/photo_gallery.html", {'all_photos': all_photos, 'album': album})

def photos(request):
    albums = PhotoAlbum.objects.all()

    context = {
        'albums': albums
    }
    return render(request, "home/layouts/gallery.html", context)


def events_view(request):
    events = Events.objects.all()
    events_meetings = Events_Meetings.objects.all()
    context = {
        "events": events,
        "events_meetings": events_meetings
    }
    return render(request, "home/layouts/events.html", context)


def video_gallery(request):
    events = Events.objects.all()
    events_meetings = Events_Meetings.objects.all()
    context = {
        "events": events,
        "events_meetings": events_meetings
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
    career = Career.objects.all()
    context  = {
        'career': career
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
        "all_company_info" : Company_info.objects.all(),
        "videos": Video.objects.all(), 
        "hero_areas": HeroArea.objects.all(),
    }
    return render (request, 'admin/pages/home_details.html', context)

@login_required
def company_info_input(request):

    try:
        company = Company_info.objects.get(id=1)
    except Company_info.DoesNotExist:
        company = None

    if request.method == "POST":
        company_name = request.POST.get("company_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        office_hours = request.POST.get("office_hours")
        friday = request.POST.get("friday")
        house_no = request.POST.get("house_no")
        block = request.POST.get("block")
        district = request.POST.get("district")
        cirtificate = request.POST.get("cirtificate")
        country = request.POST.get("country")

        if company is None:
            company = Company_info.objects.create(
                company_name=company_name,
                phone=phone,
                email=email,
                office_hours=office_hours,
                friday=friday,
                house_no=house_no,
                block=block,
                district=district,
                cirtificate=cirtificate,
                country=country
            )
        else:
            company.company_name = company_name
            company.phone = phone
            company.email = email
            company.office_hours = office_hours
            company.friday = friday
            company.house_no = house_no
            company.block = block
            company.district = district
            company.country = country
            company.save()

        messages.success(request, "Company information updated successfully!")
        return redirect("company_info_input")

    return render(request, "admin/pages/company_info_input.html", {"company": company})


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
def hero_area_input(request):
    return render (request, 'admin/pages/hero_area_input.html')

@login_required
def hero_area_update(request, id):
    hero_area = get_object_or_404(HeroArea, id=id)

    if request.method == "POST":
        hero_area.tittle = request.POST.get("tittle")
        hero_area.descriptions = request.POST.get("descriptions")

        if request.FILES.get("image"):
            hero_area.image = request.FILES.get("image")

        hero_area.save()

        messages.success(request, "Updated Successfully")
        return redirect("hero_area_input")

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
def update_vision(request, id):
     # Fetch the CoreValues object
    vision = get_object_or_404(Vision, id=id)

    if request.method == "POST":
        title = request.POST.get("title")
        descriptions = request.POST.get("descriptions")

        if not title:
            messages.error(request, "Title cannot be empty")
            return render(request, "admin/pages/update_vision.html", {"vision": vision})

        # Update fields
        vision.title = title
        vision.descriptions = descriptions

        # Handle image upload
        if request.FILES.get("image"):
            vision.image = request.FILES.get("image")

        vision.save()
        messages.success(request, "Vision has been updated successfully!")

        # Redirect to the list page after update
        return redirect("update_vision", id=vision.id)

    return render(request, "admin/pages/update_vision.html", {"vision": vision})

@login_required
def admin_mission(request):
    mission = Mission.objects.all()
    context = {
        'mission' : mission
    }
    return render(request, "admin/pages/mission.html", context)

@login_required
def update_mission(request, id):
     # Fetch the CoreValues object
    mission = get_object_or_404(Mission, id=id)

    if request.method == "POST":
        title = request.POST.get("title")
        descriptions = request.POST.get("descriptions")

        if not title:
            messages.error(request, "Title cannot be empty")
            return render(request, "admin/pages/update_vision.html", {"mission": mission})

        # Update fields
        mission.title = title
        mission.descriptions = descriptions

        # Handle image upload
        if request.FILES.get("image"):
            mission.image = request.FILES.get("image")

        mission.save()
        messages.success(request, "Vision has been updated successfully!")

        # Redirect to the list page after update
        return redirect("update_mission", id=mission.id)

    return render(request, "admin/pages/update_mission.html", {"mission": mission})

@login_required
def admin_core_values(request):
    core_values = CoreValues.objects.all()
    context = {
        'core_values': core_values
    }
    return render(request, "admin/pages/core_values.html", context)

@login_required
def update_core_values(request, id):
    # Fetch the CoreValues object
    core_value = get_object_or_404(CoreValues, id=id)

    if request.method == "POST":
        title = request.POST.get("title")
        descriptions = request.POST.get("descriptions")

        if not title:
            messages.error(request, "Title cannot be empty")
            return render(request, "admin/pages/update_core_values.html", {"core_value": core_value})

        # Update fields
        core_value.title = title
        core_value.descriptions = descriptions

        # Handle image upload
        if request.FILES.get("image"):
            core_value.image = request.FILES.get("image")

        core_value.save()
        messages.success(request, "Core Value has been updated successfully!")

        # Redirect to the list page after update
        return redirect("admin_core_values")

    # Render the update form
    return render(request, "admin/pages/update_core_values.html", {"core_value": core_value})

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
        url_1 = request.POST.get("url_1")
        url_2 = request.POST.get("url_2")

        event_title = EventTitle.objects.create(
            title=title_text,
            description=description_text
        )

        Events.objects.create(
            title=event_title,
            url_1=url_1,
            url_2=url_2
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

        info.url_1 = request.POST.get("url_1")
        info.url_2 = request.POST.get("url_2")
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


@login_required
def AdminMembersRulesDelete(request, id):
    membership = get_object_or_404(MembershipRules, id=id)

    if request.method == "POST":
        membership.delete()
        messages.success(request, "Membership Title Descriptions deleted successfully!")
        return redirect("AdminMembersRules")


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
            date=request.POST.get("date") or None,
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
        
        newses.date = request.POST.get("date") or None
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

            album.banner = random.choice(photos).image
            album.save()

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
        banner = request.FILES.get('banner')

        if title and banner:
            PhotoAlbum.objects.create(title=title, banner=banner)
            messages.success(request, "Album created successfully!")
            return redirect('admin_add_album')
        else:
            messages.error(request, "Please enter a title and select a banner image.")

    return render(request, 'admin/pages/admin_add_album.html')

@login_required
def admin_update_album(request, id):
    album = get_object_or_404(PhotoAlbum, id=id)

    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('banner')

        # Update title
        if title and title.strip() != "":
            album.title = title
            album.save()

        # Update banner image
        if file:
            album.banner = file
            album.save()

        messages.success(request, "Album updated successfully!")
        return redirect('admin_update_album', id=album.id)

    return render(request, 'admin/pages/admin_update_album.html', { 'album': album })

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
            # This catches database-level format errors and shows them as a message
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

        if title_text:
            meeting_title.title = title_text
            meeting_title.amount = amount
            meeting_title.description = description

            if image:
                meeting_title.image = image

            meeting_title.save()
            messages.success(request, "Meeting title updated successfully!")
            return redirect('admin_meeting_call')
        else:
            messages.error(request, "Title is required!")

    context = {
        'meeting_title': meeting_title
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
    email = request.GET.get('email')

    exists = User.objects.filter(email=email).exists()

    return JsonResponse({'exists': exists})

def check_phone(request):
    phone = request.GET.get('phone')

    phone_exists = Aggregator.objects.filter(phone=phone).exists()

    return JsonResponse({'phone_exists': phone_exists})
