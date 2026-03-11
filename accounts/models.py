import re, os
import hashlib
import uuid
from django.db import models
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
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


def bd_phone_validator(value):
    """Valid Bangladeshi phone number: 01XXXXXXXXX"""
    pattern = r'^01[3-9]\d{8}$'
    if not re.match(pattern, value):
        raise ValidationError("Please enter a valid mobile number (example: 01XXXXXXXXX)")

def hash_otp(otp):
    return hashlib.sha256(otp.encode()).hexdigest()

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USER_TYPES = (
        (1, "admin"),
        (2, "member"),
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

class Weekend(models.Model):
    day = models.CharField(max_length=50)

    def __str__(self):
        return self.day


class CompanyInfo(models.Model):
    company_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    office_hours = models.CharField(max_length=50)
    day_off = models.ManyToManyField(Weekend, related_name="companies", blank=True)
    house_no = models.CharField(max_length=50)
    block = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=60)
    certificate = models.ImageField(upload_to="image/", null=True, blank=True)
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



class HeroArea(models.Model):
    tittle = models.CharField(max_length=50)
    descriptions = models.TextField(null=True)
    image = models.ImageField(upload_to="media/", null=True)
    
    def __str__(self):
        return self.tittle


class AboutParagraph(models.Model):
    title = models.CharField(max_length=50)
    descriptions = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
class Vision(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to= "media/", null=True)
    descriptions = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
class Mission(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to= "media/", null=True)
    descriptions = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
class CoreValues(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to= "media/", null=True)
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
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title or "Untitled"

class Events(models.Model):
    title = models.ForeignKey(EventTitle, on_delete=models.CASCADE, null=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return str(self.title)  # returns the actual title string

    def generate_embed_url(self, url):
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

    @property
    def embed_url(self):
        return self.generate_embed_url(self.url)

class Events_Meetings(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)

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
    slug = models.SlugField(max_length=60, unique=True, blank=True) 
    image = models.ImageField(upload_to="news/", null=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)



class Career(models.Model):
    title = models.CharField( max_length=50)
    description = models.TextField(null=True)

    def __str__(self):
        return self.title

class TempMember(models.Model):
    PAYMENT_CHOICES = [
        ('pending', 'pending'),
    ]
    company_name = models.CharField(max_length=50)
    person_name = models.CharField(max_length=50)
    designation = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    is_aggregator = models.CharField(max_length=4,null=True, blank=True)
    brtc_licence_no = models.CharField(max_length=50, blank=True)
    mobile = models.CharField(max_length=15,validators=[bd_phone_validator],blank=True,unique=True)
    phone = models.CharField(max_length=20,blank=True, null=True)
    n_id = models.CharField(max_length=22,null=True)
    appoinment_letter = models.FileField(upload_to="letter/", blank=True, null=True)
    cv = models.FileField(upload_to="cv/", blank=True, null=True)
    address = models.TextField(blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='pending')
    password = models.CharField(max_length=128)
    otp = models.CharField(max_length=64, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.person_name



class Aggregator(models.Model):

    USER_TYPE_CHOICES = [
        (1, 'AGM'),
        (2, 'AGU')
    ]
    STATUS_CHOICES = [
        (1, 'unverified'),
        (2, 'verified')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="aggregators")

    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, editable=False, null=True)
    member_id = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    image = models.ImageField(upload_to="Aggregator/", null=True)
    company_logo = models.ImageField(upload_to="Aggregator/", null=True)
    designation = models.CharField(max_length=50, null=True)
    is_aggregator = models.CharField(max_length=3, null=True)  
    status = models.IntegerField(choices=USER_TYPE_CHOICES, editable=False, null=True, default=1)
    mobile = models.CharField(max_length=15, validators=[bd_phone_validator], blank=True, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    brtc_licence_no = models.CharField(max_length=50, blank=True)
    tread_licence_no = models.CharField(max_length=50, blank=True, null=True)
    n_id = models.CharField(max_length=22, null=True)

    appoinment_letter = models.FileField(upload_to="letter/", blank=True, null=True)
    cv = models.FileField(upload_to="cv/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    address = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_type', 'member_id'], name='unique_member_per_type')
        ]

    def save(self, *args, **kwargs):
        # Set user_type (1 = AGM, 2 = AGU)
        if self.is_aggregator == "Yes":
            self.user_type = 1
        else:
            self.user_type = 2

        # Generate member_id (number only)
        if not self.member_id:
            last = Aggregator.objects.filter(user_type=self.user_type).order_by('-id').first()
            if last and last.member_id:
                try:
                    new_number = int(last.member_id) + 1
                except ValueError:
                    new_number = 100
            else:
                new_number = 100
            self.member_id = str(new_number)

        # Generate slug from company_name
        if not self.slug and self.company_name:
            self.slug = slugify(self.company_name)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member_id} - {self.name}"


class PhotoAlbum(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(null= True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)  
    banner = models.ImageField(upload_to="gallery/")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)



def photo_upload_to(instance, filename):
    ext = filename.split('.')[-1]  # get file extension
    if instance.slug:
        # use the slug in the filename
        filename = f"{instance.slug}.{ext}"
    else:
        import time
        filename = f"{int(time.time())}.{ext}"  # fallback for new object
    return os.path.join("gallery/", filename)

class Photo(models.Model):
    album = models.ForeignKey(PhotoAlbum, on_delete=models.CASCADE, related_name="photos", null=True)
    image = models.ImageField(upload_to=photo_upload_to)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)  # slug field

    def __str__(self):
        return f"{self.album.title} - Photo {self.id}"

    def save(self, *args, **kwargs):
        # generate slug if not exists
        if not self.slug and self.album:
            base_slug = slugify(self.album.title)
            count = Photo.objects.filter(album=self.album).count() + 1
            self.slug = f"SISPAB-{base_slug}-{count}"
        super().save(*args, **kwargs)



class MeetingTitle(models.Model):
    title = models.CharField(max_length=80, null=True, blank=False)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    amount = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)  # TextField for long text
    image = models.ImageField(upload_to="image/", null=True, blank=True)
    expire_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            # Generate base slug from title
            base_slug = slugify(self.title)[:75]  # reserve space for uniqueness
            slug = base_slug
            # Ensure slug is unique
            while MeetingTitle.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{uuid.uuid4().hex[:5]}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title if self.title else "No Title"


class MeetingCall(models.Model):

    PAYMENT_CHOICES = [
        ('bkash', 'Bkash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    title = models.ForeignKey("MeetingTitle", on_delete=models.CASCADE, null=True, related_name="calls")
    company_name = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    no_of_person = models.PositiveIntegerField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    transection_id = models.CharField(max_length=255)
    amount = models.IntegerField(null=True, blank=True)
    payout_number = models.CharField(max_length=20, null=True)
    screenshot = models.ImageField(upload_to="payment/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title.title} - {self.name}"
    

class Seo(models.Model):
    page_name = models.CharField(max_length=100, unique=True)

    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()
    meta_keywords = models.TextField(blank=True)

    meta_image = models.ImageField(upload_to="seo/", blank=True, null=True)
    meta_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.page_name
    
class GovermentServices(models.Model):
    title = models.CharField(max_length=50, null= True)
    url = models.URLField(max_length=200)
    def __str__(self):
        return self.title

class EmergencyServices(models.Model):
    title = models.CharField(max_length=50, null=True)
    number = models.URLField(max_length=200)
    def __str__(self):
        return self.title
    
class BecomeMember(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(null=True)
    def __str__(self):
        return self.title


class Sponsor(models.Model):
    sponsor_name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, null=True)
    designation = models.CharField(max_length=200, null=True)
    sponsor_email = models.EmailField()
    sponsor_phone = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    company_logo = models.ImageField(upload_to="sponsor_logo/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sponsor_name
    