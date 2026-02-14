import re
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        if "user_type" not in extra_fields:
            extra_fields["user_type"] = 1 

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", 1)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USER_TYPES = (
        (1, "admin"),
        (2, "member")
    )
    user_type = models.IntegerField(choices=USER_TYPES)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Gellary(models.Model):
    gellary_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="media/", null=True)
    image1 = models.ImageField(upload_to="media/", null=True)
    image2 = models.ImageField(upload_to="media/", null=True)
    year = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    
    def __str__(self):
        return self.gellary_name

class Company_info(models.Model):
    company_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    office_hours = models.CharField(max_length=50)
    friday = models.CharField(max_length=50)
    house_no = models.CharField(max_length=50)
    block = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=60)
    cirtificate = models.ImageField(upload_to="image/", null=True)
    country = models.CharField(max_length=50)
    
    def __str__(self):
        return self.company_name

class Video(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def embed_url(self):
        si_param = "FzYOnU1EAQsQ4JFe" 
        if "youtube.com/embed/" in self.url:
            clean_url = re.sub(r'\?si=.*', '', self.url)
            return f"{clean_url}?si={si_param}"

        youtube_regex = (
            r'(?:https?://)?(?:www\.)?'
            r'(?:youtube\.com/watch\?v=|youtu\.be/)'
            r'([A-Za-z0-9_-]{11})'
        )
        match = re.search(youtube_regex, self.url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}?si={si_param}"

        return self.url



class Goal(models.Model):
    goal_tittle = models.CharField(max_length=50)
    goal_descriptions = models.TextField(null=True)
    
    def __str__(self):
        return self.goal_tittle


class AboutParagraph(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
class Vision(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
class Mission(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
class CoreValues(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.title

class AboutAlbum(models.Model):
    title = models.CharField(max_length=50)
    image_1 = models.ImageField(upload_to="about/", null=True)
    image_2 = models.ImageField(upload_to="about/", null=True)
    image_3 = models.ImageField(upload_to="about/", null=True)
    descriptions = models.TextField(null=True)

    def __str__(self):
        return self.title

class Co_sponsers(models.Model):
    image_1 = models.ImageField(upload_to="image/", null=True)
    image_2 = models.ImageField(upload_to="image/", null=True)
    image_3 = models.ImageField(upload_to="image/", null=True)
    image_4 = models.ImageField(upload_to="image/", null=True)
    image_5 = models.ImageField(upload_to="image/", null=True)
    
    def __str__(self):
        return f"Sponsor Set #{self.id}"
    
class FoundersInfo(models.Model):
    founder_name = models.CharField(max_length=50)
    founder_image = models.ImageField(upload_to="image/", null=True)
    designation = models.CharField(max_length=50)
    company = models.CharField(max_length=50)
    
    def __str__(self):
        return self.founder_name
    
    
class SispabExecutiveCom(models.Model):
    name = models.CharField(max_length=50, null=True)
    position = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to="image/", null=True)
    
    def __str__(self):
        return self.name

class PreviousExecutiveCommittee(models.Model):
    name = models.CharField(max_length=50, null=True)
    designation = models.CharField(max_length=50, null= True)
    position = models.CharField(max_length=50, null=True)
    company = models.CharField(max_length = 50, null=True)
    image = models.ImageField(upload_to="image/", null=True)
    
    def __str__(self):
        return self.name
    
class EventTitle(models.Model):
   title = models.CharField(max_length=200, null= True)
   description = models.TextField(blank=True, null=True)
   def __str__(self):
       return self.title

class Events(models.Model):
    title = models.ForeignKey(EventTitle, on_delete=models.CASCADE, null=True)
    url_1 = models.URLField(null=True, blank=True)
    url_2 = models.URLField(null=True, blank=True)
   

    def __str__(self):
        return self.title
    
    def generate_embed_url(self, url):
        if not url:
            return None

        si_param = "FzYOnU1EAQsQ4JFe"

        if "youtube.com/embed/" in url:
            clean_url = re.sub(r'\?si=.*', '', url)
            return f"{clean_url}?si={si_param}"

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

    @property
    def embed_url_1(self):
        return self.generate_embed_url(self.url_1)

    @property
    def embed_url_2(self):
        return self.generate_embed_url(self.url_2)


class Events_Meetings(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    # --- Helper method to generate embed URL ---
    def generate_embed_url(self, url):
        if not url:
            return None

        si_param = "FzYOnU1EAQsQ4JFe"

        # If already an embed URL
        if "youtube.com/embed/" in url:
            clean_url = re.sub(r'\?si=.*', '', url)
            return f"{clean_url}?si={si_param}"

        # Match normal or short YouTube URLs
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

    # --- Properties for each URL ---
    @property
    def embed_url(self):
        return self.generate_embed_url(self.url)

    

class PhotoGallery(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="media/")
    year = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.title

class Blog(models.Model):
    image = models.ImageField(upload_to="media/",  null=True)
    title = models.CharField(max_length=60)
    date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True)
    
    def __str__(self):
        return self.title
    

bd_phone_validator = RegexValidator(
    regex=r'^(?:\+8801|01)[3-9]\d{8}$',
    message="Enter a valid Bangladesh phone number (e.g. 017XXXXXXXX or +88017XXXXXXXX)"
)

class ComplainList(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    phone = models.CharField(
        max_length=15, validators=[bd_phone_validator], null=True, blank=True
    )
    issue = models.TextField(null=True, blank=True)
    suggestion = models.CharField(max_length=50, null=True, blank=True)
    aggregator = models.ForeignKey('Aggregator', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.aggregator.name}"

    
class Contact_list(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    address = models.TextField(null=True)
    business_name = models.CharField(max_length=50)
    message = models.TextField(null=True)
    
    def __str__(self):
        return f"{self.name} - {self.business_name}"



class MembershipRules(models.Model):
    title = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    rules = models.TextField(null=True)

    def __str__(self):
        return self.title
    

class News(models.Model):
    title = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to="news/", null=True)
    date = models.DateField(null = True)
    description = models.TextField(null=True)

    def __str__(self):
        return self.title
    

class Career(models.Model):
    position_name = models.CharField( max_length=50)
    num_of_vacancy = models.IntegerField(null=True, blank=True)
    loction_add = models.TextField(null=True)
    deadline_date = models.DateField(null=True)
    job_type = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.position_name
    


class Aggregator(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="aggregators")
    name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=50)
    phone = models.CharField(
        max_length=15,
        validators=[bd_phone_validator],
        blank=True
    )
    brtc_licence_no = models.CharField(
        max_length=50,
        blank=True
    )
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.company_name})"
    

class PhotoAlbum(models.Model):
    title = models.CharField(max_length=100, unique=True)
    banner = models.ImageField(upload_to="gallery/")

    def __str__(self):
        return self.title


class Photo(models.Model):
    album = models.ForeignKey(PhotoAlbum, on_delete=models.CASCADE, related_name="photos", null=True)
    image = models.ImageField(upload_to="gallery/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.album.title} - Photo {self.id}"
