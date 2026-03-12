from .views import *
from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),

    # home_url start
    
    path('', home_view, name = 'home' ),
    path('about/',about_view, name = 'about' ),
    path('vision/',vision, name = 'vision' ),
    path('core_values/',core_values, name = 'core_values' ),
    path('mission/',mission, name = 'mission' ),
    path('founder/',founder_view, name = 'founder' ),
    path('current_executive_commitee/',current_executive_commitee, name = 'current_executive_commitee' ),
    path('previous_committee/',previous_committee, name = 'previous_committee' ),
    path('benefit_od_member/',benefit_od_member, name = 'benefit_od_member' ),
    path('sisbup_secretariat/',sisbup_secretariat, name = 'sisbup_secretariat' ),
    path('advisory_council/',advisory_council, name = 'advisory_council' ),
    path('member_resistation/',member_resistation, name = 'member_resistation' ),
    path('membership_rules/',membership_rules, name = 'membership_rules' ),
    path('process_of_members/',process_of_members, name = 'process_of_members' ),
    path('login/', login_view, name = 'login' ),
    path('logout/', logout_view, name='logout'),
    path('registration/', registration_view, name = 'registration' ),
    path('contact/', contact_view, name = 'contact' ),
    path('blog/', blog_view, name = 'blog' ),
    path('view_more/<int:id>/',view_more, name='view_more'),
    path('news/', news_view, name = 'news' ),
    path("news/<slug:slug>/", news_detail_view, name="news_detail_view"),
    path('complain/', complain_view, name = 'complain' ),
    path('media/', media_view, name = 'media' ),

    path('photos/<slug:slug>/', photo_gallery, name = 'photos' ),
    path('photo/', photos, name = 'photo' ),

    path('events/', events_view, name = 'events' ),
    path('video_gallery/', video_gallery, name = 'video_gallery' ),
    path('meetings/', meetings, name = 'meetings' ),
    path('contact_submit/', contact_submit, name = 'contact_submit' ),
    path('career/', career, name = 'career' ),
    path('meeting_call/<slug:slug>/', meeting_call, name = 'meeting_call' ),
    path('meeting_calls/', meeting_calls, name = 'meeting_calls' ),
    path('membership_list/', membership_list, name = 'membership_list' ),
    path('member_detail/<slug:slug>/', member_detail, name='member_detail'),

    path('search/', search, name = 'search' ),
    path('profile/', profile, name = 'profile' ),
    path('edit_profile/', edit_profile, name = 'edit_profile' ),

    #api
    path('check_email/',check_email, name='check_email'),
    path('resend_otp/',resend_otp, name='resend_otp'),
    path('check_phone/',check_phone, name='check_phone'),
    path('check_company/',check_company, name='check_company'),
    path("get_aggregator_info/", get_aggregator_info, name="get_aggregator_info"),
    path("sponser_list/", sponser_list, name="sponser_list"),
    path("become_a_member/", become_a_member, name="become_a_member"),

    
    #home_url end



    #admin_url start
    
    path('dashboard/', dashboard, name = 'dashboard' ),
    path('company_info_input/', company_info_input, name = 'company_info_input' ),
    path('company_info_input/<int:id>/', company_info_input, name = 'company_info_input' ),
    path('home_details/', home_details, name = 'home_details' ),
    path("video/add/", video_input, name="video_add"),
    path("video/edit/<int:id>/", video_input, name="video_input"),

    path('gallry_input/', gallry_input, name = 'gallry_input' ),
    path('gallry_update/<int:gellary_id>/', gallry_update, name='gallry_update'),
    path('gallry_delete/<int:gellary_id>/', gallry_delete, name='gallry_delete'),

    path('hero_area_input/', hero_area_input, name='hero_area_input'),
    path('hero_area_input/<int:id>/', hero_area_input, name='hero_area_update'),


    path('about_details/', about_details, name='about_details'),
    path('album_input/', album_input, name='album_input'),

    
    path('update_story/<int:id>/', update_story, name='update_story'),

    path("admin_vision/", admin_vision, name="admin_vision"),
    path("admin_vision/add/", update_vision, name="add_vision"),
    path("admin_vision/edit/<int:id>/", update_vision, name="update_vision"),

    path("admin_mission/", admin_mission, name="admin_mission"),
    path("mission/add/", mission_input, name="add_mission"),
    path("mission/edit/<int:id>/", mission_input, name="update_mission"),

    path("admin_core_values/", admin_core_values, name="admin_core_values"),
    path("core_values/add/", update_core_values, name="add_core_values"),
    path("core_values/update/<int:id>/", update_core_values, name="update_core_values"),


    path('album_update/<int:id>/', album_update, name='album_update'),
    path('album_delete/<int:id>/', album_delete, name='album_delete'),


    path('co_sponsers', co_sponsers, name='co_sponsers'),
    path('sponser_update/<int:id>/', sponser_update, name='sponser_update'),
    path('sponser_delete/<int:id>/', sponser_delete, name='sponser_delete'),
    
    
    path('sispab_founders', sispab_founders, name='sispab_founders'),
    path('add_founder', add_founder, name='add_founder'),
    path('founder_update/<int:id>/', founder_update, name='founder_update'),
    path('founder_delete/<int:id>/', founder_delete, name='founder_delete'),
    

    path('sispab_executive_com//', sispab_executive_com, name='sispab_executive_com'),
    path('add_sispab_executive_com//', add_sispab_executive_com, name='add_sispab_executive_com'),
    path('sispab_executive_com_update/<int:id>/', sispab_executive_com_update, name='sispab_executive_com_update'),
    path('sispab_executive_com_delete/<int:id>/', sispab_executive_com_delete, name='sispab_executive_com_delete'),



    path('previous_executive_committee/', previous_executive_committee, name='previous_executive_committee'),
    path('add_previous_executive_committee/', add_previous_executive_committee, name='add_previous_executive_committee'),
    path('previous_executive_committee_update/<int:id>/', previous_executive_committee_update, name='previous_executive_committee_update'),
    path('previous_executive_committee_delete/<int:id>/', previous_executive_committee_delete, name='previous_executive_committee_delete'),


    path('AdminEvents/', AdminEvents, name='AdminEvents'),

    path('admin_video_gallery/', admin_video_gallery, name='admin_video_gallery'),
    path('upload_video/', upload_video, name='upload_video'),
    path('video_update/<int:id>/', video_update, name='video_update'),
    path('video_delete/<int:id>/', video_delete, name='video_delete'),
    
    path("meeting_create/", meeting_create, name="meeting_create"),
    path("meeting_video_update/<int:id>/", meeting_update, name="meeting_video_update"),
    path("meeting_video_delete/<int:id>/", meeting_delete, name="meeting_video_delete"),
    
    path("AdminMedia/", AdminMedia, name="AdminMedia"),
    path("AdminMediaUpload/", AdminMediaUpload, name="AdminMediaUpload"),
    path("AdminMediaUpdate/<int:id>/", AdminMediaUpdate, name="AdminMediaUpdate"),
    path("AdminMediaDelete/<int:id>/", AdminMediaDelete, name="AdminMediaDelete"),
    
    
    
    path('AdminBlog/', AdminBlog, name='AdminBlog'),
    path('add_blogs/', add_blogs, name='add_blogs'),
    path('blog_update/<int:id>/', blog_update, name='blog_update'),
    path('blog_delete/<int:id>/', blog_delete, name='blog_delete'),
    
    
    
    path('AdminCampain/', AdminCampain, name='AdminCampain'),
    path('complain_update/<int:id>/', complain_update, name='complain_update'),
    path('complain_delete/<int:id>/', complain_delete, name='complain_delete'),
    
    path('AdminContact/', AdminContact, name='AdminContact'),
    path('contact_update/<int:id>/', contact_update, name='contact_update'),
    path('contact_delete/<int:id>/', contact_delete, name='contact_delete'),
    
    path('AdminMembersRules/', AdminMembersRules, name='AdminMembersRules'),
    path('AdminMembersRulesAdd/', AdminMembersRulesAdd, name='AdminMembersRulesAdd'),
    path('AdminMembersRulesUpdate/<int:id>/', AdminMembersRulesUpdate, name='AdminMembersRulesUpdate'),

    path('admin_membership_list/', admin_membership_list, name='admin_membership_list'),
    path('admin_membership_list_details/<int:id>', admin_membership_list_details, name='admin_membership_list_details'),

    path('admin_photo_list/<int:id>/', admin_photo_list, name='admin_photo_list'),
    path('admin_add_photo/<int:id>', admin_add_photo, name='admin_add_photo'),
    path('admin_update_photo/<int:id>/', admin_update_photo, name='admin_update_photo'),
    path('delete_photo/<int:id>/', delete_photo, name='delete_photo'),


    
    path('admin_Album_list/', admin_Album_list, name='admin_Album_list'),
    path('admin_add_album/', admin_add_album, name='admin_add_album'),
    path('admin_update_album/<int:id>/', admin_update_album, name='admin_update_album'),
    path('delete_album/<int:id>/', delete_album, name='delete_album'),

    path('admin_career/', admin_career, name='admin_career'),
    path('admin_add_career/', admin_add_career, name='admin_add_career'),
    path('admin_update_career/<int:id>/', admin_update_career, name='admin_update_career'),
    path('admin_delete_career/<int:id>/', admin_delete_career, name='admin_delete_career'),

    path('AdminNews/', AdminNews, name='AdminNews'),
    path('AdminAddNews/',AdminAddNews, name='AdminAddNews'),
    path('news_update/<int:id>',AdminUpdateNews, name='news_update'),
    path('news_delete/<int:id>',AdminNewswDelete, name='news_delete'),


    path('meeting_call_list/<int:id>/', meeting_call_list, name = 'meeting_call_list'),
    path('admin_meeting_call/', admin_meeting_call, name = 'admin_meeting_call'),
    path('meeting_call_add/', meeting_call_add, name = 'meeting_call_add'),
    path('meeting_call_update/<int:id>/', meeting_call_update, name = 'meeting_call_update'),
    path('meeting_call_delete/<int:id>/', meeting_call_delete, name = 'meeting_call_delete'),
    
    path('call_delete/<int:id>/', call_delete, name = 'call_delete'),
    path('call_update/<int:id>/', call_update, name = 'call_update'),

    path('admin_member_registration_list_details/<int:id>/', admin_member_registration_list_details, name = 'admin_member_registration_list_details'), 
    path('accept/<int:id>/', accept, name = 'accept'),
    path('reject/<int:id>/', reject, name = 'reject'),

    path('approve/<int:id>/', approve, name = 'approve'),
    path('reject_member/<int:id>/', reject_member, name = 'reject_member'),
    
    path('admin_become_a_member/', admin_become_a_member, name = 'admin_become_a_member'),
    path('mem/create/', admin_become_a_member_form, name='create'),
    path('mem/update/<int:id>/', admin_become_a_member_form, name='update'),
    path('mem/delete/<int:id>/', delete_become_a_member, name='delete_become_a_member'),
    
    path('admin_sponser_list/', admin_sponser_list, name = 'admin_sponser_list'),
    path('sponsor/create/', sponsor_form, name='create_sponsor'),
    path('sponsor/update/<int:id>/', sponsor_form, name='update_sponsor'),
    path('sponsor/delete/<int:id>/', delete_sponsor, name='admin_delete_sponsor'),

    path('government_services/', government_services, name='government_services'),
    path('government_services/create/', government_services_forms, name='create_government_services'),
    path('government_services/update/<int:id>/', government_services_forms, name='update_government_services'),
    path('government_services/delete/<int:id>/', delete_government_services, name='admin_delete_government_services'),
    
    path('emergency_services/', emergency_services, name='emergency_services'),
    path('emergency_services/create/', emergency_services_forms, name='create_emergency_services'),
    path('emergency_services/update/<int:id>/',emergency_services_forms, name='update_emergency_services'),
    path('emergency_services/delete/<int:id>/', delete_emergency_services, name='admin_delete_emergency_services'),
    
    
    
    path('seo/', seo, name = 'seo'),
    path('add_seo/', add_seo, name = 'add_seo'),
    path('edit_seo/<int:id>/', edit_seo, name = 'edit_seo'),
    #admin_url end
]
