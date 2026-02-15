from django.contrib import admin
from .views import *
from django.urls import path

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
    path("news_detail_view/<int:id>/", news_detail_view, name="news_detail_view"),
    path('complain/', complain_view, name = 'complain' ),
    path('media/', media_view, name = 'media' ),

    path('photos/<int:id>/', photo_gallery, name = 'photos' ),
    path('photo/', photos, name = 'photo' ),

    path('events/', events_view, name = 'events' ),
    path('video_gallery/', video_gallery, name = 'video_gallery' ),
    path('meetings/', meetings, name = 'meetings' ),
    path('contact_submit/', contact_submit, name = 'contact_submit' ),

    
    #home_url end


    #admin_url start
    
    path('dashboard/', dashboard, name = 'dashboard' ),
    path('company_info_input/', company_info_input, name = 'company_info_input' ),
    path('home_details/', home_details, name = 'home_details' ),
    path('video_input/<int:id>/', video_input, name = 'video_input' ),

    path('gallry_input/', gallry_input, name = 'gallry_input' ),
    path('gallry_update/<int:gellary_id>/', gallry_update, name='gallry_update'),
    path('gallry_delete/<int:gellary_id>/', gallry_delete, name='gallry_delete'),

    path('hero_area_input/', hero_area_input, name = 'hero_area_input' ),
    path('hero_area_update/<int:id>/', hero_area_update, name='hero_area_update'),


    path('about_details/', about_details, name='about_details'),
    path('album_input/', album_input, name='album_input'),

    path('update_story/<int:id>/', update_story, name='update_story'),
    path('update_vision/<int:id>/', update_vision, name='update_vision'),
    path('update_mission/<int:id>/', update_mission, name='update_mission'),
    path('update_core_values/<int:id>/', update_core_values, name='update_core_values'),


    path('album_update/<int:id>/', album_update, name='album_update'),
    path('album_delete/<int:id>/', album_delete, name='album_delete'),


    path('co_sponsers', co_sponsers, name='co_sponsers'),
    path('sponser_update/<int:id>/', sponser_update, name='sponser_update'),
    path('sponser_delete/<int:id>/', sponser_delete, name='sponser_delete'),
    
    
    path('sispab_founders', sispab_founders, name='sispab_founders'),
    path('add_founder', add_founder, name='add_founder'),
    path('founder_update/<int:id>/', founder_update, name='founder_update'),
    path('founder_delete/<int:id>/', founder_delete, name='founder_delete'),
    

    path('sispab_executive_com', sispab_executive_com, name='sispab_executive_com'),
    path('add_sispab_executive_com', add_sispab_executive_com, name='add_sispab_executive_com'),
    path('sispab_executive_com_update/<int:id>/', sispab_executive_com_update, name='sispab_executive_com_update'),
    path('sispab_executive_com_delete/<int:id>/', sispab_executive_com_delete, name='sispab_executive_com_delete'),



    path('previous_executive_committee', previous_executive_committee, name='previous_executive_committee'),
    path('add_previous_executive_committee', add_previous_executive_committee, name='add_previous_executive_committee'),
    path('previous_executive_committee_update/<int:id>/', previous_executive_committee_update, name='previous_executive_committee_update'),
    path('previous_executive_committee_delete/<int:id>/', previous_executive_committee_delete, name='previous_executive_committee_delete'),


    path('AdminEvents', AdminEvents, name='AdminEvents'),
    path('upload_video', upload_video, name='upload_video'),
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
    
    
    
    path('AdminCampain', AdminCampain, name='AdminCampain'),
    path('complain_update/<int:id>/', complain_update, name='complain_update'),
    path('complain_delete/<int:id>/', complain_delete, name='complain_delete'),
    
    path('AdminContact', AdminContact, name='AdminContact'),
    path('contact_update/<int:id>/', contact_update, name='contact_update'),
    path('contact_delete/<int:id>/', contact_delete, name='contact_delete'),
    
    path('AdminMembersRules/', AdminMembersRules, name='AdminMembersRules'),
    path('AdminMembersRulesAdd/', AdminMembersRulesAdd, name='AdminMembersRulesAdd'),
    path('AdminMembersRulesUpdate/<int:id>/', AdminMembersRulesUpdate, name='AdminMembersRulesUpdate'),
    path('AdminMembersRulesDelete/<int:id>/', AdminMembersRulesDelete, name='AdminMembersRulesDelete'),

    path('admin_photo_list/<int:id>/', admin_photo_list, name='admin_photo_list'),
    path('admin_add_photo/<int:id>', admin_add_photo, name='admin_add_photo'),
    path('admin_update_photo/<int:id>/', admin_update_photo, name='admin_update_photo'),
    path('delete_photo/<int:id>/', delete_photo, name='delete_photo'),


    
    path('admin_Album_list/', admin_Album_list, name='admin_Album_list'),
    path('admin_add_album/', admin_add_album, name='admin_add_album'),
    path('admin_update_album/<int:id>/', admin_update_album, name='admin_update_album'),
    path('delete_album/<int:id>/', delete_album, name='delete_album'),

 


    path('AdminNewa/', AdminNewa, name='AdminNewa'),
    path('AdminAddNews/',AdminAddNews, name='AdminAddNews'),
    path('news_update/<int:id>',AdminUpdateNews, name='news_update'),
    path('news_delete/<int:id>',AdminNewswDelete, name='news_delete'),

    #admin_url end
]
