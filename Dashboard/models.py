from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from User.models import Seller

# define the models of category
class Category(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}"

# define the model of a auction list
class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=512)
    address = models.CharField(max_length=255)
    starting_bid = models.IntegerField()
    current_bid = models.IntegerField(default=0)
    current_bid_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, related_name='bids_made')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="auction_category", blank=True, null=True) 
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="auction_seller")
    creation_date = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    house_size = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='images/auction_item_images/')
    winner = models.ForeignKey(User, related_name='won_auctions', on_delete=models.SET_NULL, null=True, blank=True)
    papers_confirmed = models.BooleanField(default=False)
    purchase_success = models.BooleanField(default=False)
    start_time = models.DateTimeField(default=timezone.now)
    refund_requested = models.BooleanField(default=False)
    refund_requested_time = models.DateTimeField(null=True, blank=True)
  
    

    APPROVAL_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')

    def __str__(self):
        return f"Auction id: {self.id} | Title: {self.title} | Seller: {self.seller} | Status: {self.approval_status}"
    
    def get_fields(self):
        return [(field.name, getattr(self, field.name)) for field in Auction._meta.fields]
    
    @classmethod
    def get_past_auctions(cls):
        return cls.objects.filter(end_time__lt=timezone.now())
    @property
    def is_upcoming(self):
        return self.creation_date > timezone.now()
    
   


# define the model of a bid
class Bid(models.Model):
    bider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid_date = models.DateTimeField(auto_now_add=True)
    bid_price = models.IntegerField()
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auction_bids")

    def __str__(self):
        return f"{self.bider} bid ${self.bid_price} on {self.auction}"