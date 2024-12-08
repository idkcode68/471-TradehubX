from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone

from .models import Auction, Bid,Comment, Watchlist
from .forms import NewCommentForm,BidForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

# views.py
# views.py

from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from .models import Auction, Bid, Comment, Watchlist
from .forms import NewCommentForm
from django.contrib.auth.decorators import login_required

def AuctionItem(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    now = timezone.now()
    time_left = auction.end_time - now
    seconds_left = time_left.total_seconds()

    # Ensure the auction is still active
    if seconds_left < 0:
        seconds_left = 0

    # Other existing code for getting bids, comments, etc.
    bid_Num = Bid.objects.filter(auction=auction_id).count()
    comments = Comment.objects.filter(auction=auction_id).order_by("-cm_date")
    highest_bid = Bid.objects.filter(auction=auction_id).order_by("-bid_price").first()
    watching = False
    if request.user.is_authenticated and Watchlist.objects.filter(user=request.user, auctions=auction):
        watching = True

    if request.method == "GET":
        commentForm = NewCommentForm()
        return render(request, "AuctionItem.html", {
            "auction": auction,
            "user": request.user,
            "bid_Num": bid_Num,
            "commentForm": commentForm,
            "comments": comments,
            "watching": watching,
            "seconds_left": seconds_left,
        })
   
def LiveAuction(request):
    live_auctions = Auction.objects.filter(
        approval_status='approved',
        end_time__gt=timezone.now()
    ).exclude(creation_date__gt=timezone.now()).order_by('-creation_date')
    return render(request, "searchresults.html", {"auctions": live_auctions, 'name': 'Live Auction'})

def UpcomingAuction(request):
    upcoming_auctions = Auction.objects.filter(
        approval_status='approved',
        creation_date__gt=timezone.now()
    ).order_by('-creation_date')
    return render(request, "searchresults.html", {"auctions": upcoming_auctions, 'name': 'Upcoming Auction'})

def past_auctions(request):
    past_auctions = Auction.objects.filter(approval_status='approved',end_time__lt=timezone.now()).order_by('-creation_date')
    
    for auction in past_auctions:
        if not auction.winner:
            highest_bid = Bid.objects.filter(auction=auction).order_by('-bid_price').first()
            if highest_bid:
                auction.winner = highest_bid.bider
                auction.current_bid = highest_bid.bid_price
                auction.save()
                # Send an automated winner notification
                send_mail(
                    'Congratulations! You Won the Auction',
                    f'Dear {auction.winner.username},\n\nYou have won the auction for {auction.title} with a bid of ${auction.current_bid}.\n\nThank you for participating!',
                    'no-reply@auctionwebsite.com',
                    [auction.winner.email],
                    fail_silently=False,
                )
    return render(request, 'searchresults.html', {"auctions": past_auctions, 'name':'Past Auction'})

from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Auction, Bid
from .forms import BidForm

@login_required
def bitplacement(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = BidForm(request.POST)
        
        try:
            bid_price = Decimal(request.POST.get('bid_price', '0'))
        except InvalidOperation:
            return JsonResponse({
                'success': False,
                'message': 'Invalid bid amount. Please enter a valid number.'
            })

        if bid_price > Decimal(auction.starting_bid):
            try:
                new_bid = Bid(
                    bider=request.user,
                    bid_date=timezone.now(),
                    auction=auction,
                    bid_price=bid_price
                )
                new_bid.save()

                auction.current_bid = bid_price
                auction.save()

                bidder_email = request.user.email
                if bidder_email:
                    subject = f'Your Bid Placed on "{auction.title}"'
                    message = (
                        f'Dear {request.user.username},\n\n'
                        f'You have successfully placed a bid on the auction "{auction.title}".\n\n'
                        f'Bid Amount: ${bid_price:.2f}\n'
                        f'Bid Date: {new_bid.bid_date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
                        f'Thank you for using our auction platform.\n'
                    )
                    

                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [bidder_email],
                        fail_silently=False,
                    )

                    print(f'Email sent successfully to {bidder_email}')

                # Notify previous bidders
                all_bids = Bid.objects.filter(auction=auction).exclude(bider=request.user).order_by('-bid_date')
                seen_bidders = set()
                for bid in all_bids:
                    if bid.bider not in seen_bidders:
                        seen_bidders.add(bid.bider)
                        previous_bidder_email = bid.bider.email
                        if previous_bidder_email:
                            notification_subject = f'Your bid has been outbid on "{auction.title}"'
                            notification_message = (
                                f'Dear {bid.bider.username},\n\n'
                                f'Your bid on "{auction.title}" has been outbid.\n\n'
                                f'Your bid was: ${bid.bid_price:.2f}\n'
                                f'The new bid is: ${bid_price:.2f}\n\n'
                                f'If you want to outbid it, please place a new bid.\n\n'
                                f'Thank you for using our auction platform.\n'
                            )

                            send_mail(
                                notification_subject,
                                notification_message,
                                settings.EMAIL_HOST_USER,
                                [previous_bidder_email],
                                fail_silently=False,
                            )

                            print(f'Notification email sent to previous bidder {previous_bidder_email}')

                return JsonResponse({
                    'success': True,
                    'current_bid': f'${bid_price:.2f}',
                    'message': 'Your bid has been placed successfully!',
                    'bidder': request.user.username,
                    'bid_price': f'${bid_price:.2f}',
                    'bid_date': timezone.localtime(new_bid.bid_date).strftime('%Y-%m-%d %H:%M:%S')  # Local time
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error: {str(e)}'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Your bid must be higher than the starting bid.'
            })

    # Display only the latest 5 bids initially
    bids = Bid.objects.filter(auction=auction).order_by('-bid_date')[:5]
    bid_form = BidForm()
    context = {
        'auction': auction,
        'bids': bids,
        'bid_form': bid_form,
        'has_next': Bid.objects.filter(auction=auction).count() > 5  # Check if there are more bids
    }
    return render(request, 'bitplacement.html', context)

from django.http import JsonResponse
from django.core.serializers import serialize

def load_bids(request, auction_id):
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 5))
    bids = Bid.objects.filter(auction_id=auction_id).select_related('bider').order_by('-bid_date')[offset:offset + limit]

    bid_data = []
    for bid in bids:
        bid_data.append({
            'bider': bid.bider.username,
            'bid_price': bid.bid_price,
            'bid_date': bid.bid_date.strftime('%Y-%m-%d %H:%M:%S')  # Format date as needed
        })

    has_next = Bid.objects.filter(auction_id=auction_id).count() > offset + limit

    return JsonResponse({
        'bids': bid_data,
        'has_next': has_next
    })
    
from django.shortcuts import render
from .models import Auction

def search_auctions(request):
    query = request.GET.get('search', '')
    auctions = Auction.objects.all()
    
    if query:
        auctions = auctions.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query) |
            Q(starting_bid__icontains=query)
        )

    context = {
        'auctions': auctions
    }
    return render(request, 'dashboard/home.html', context)

def adminapprove(request):
    pending_auction= Auction.objects.filter(approval_status='pending')
    if request.method=='POST':
        action_value = request.POST.get('action')
        action,data=action_value.split('|')
        preauction= Auction.objects.get(pk=data)
        preauction.approval_status=action
        seller=preauction.seller
        if action == 'approved':
            seller.total_properties+=1
            seller.save()
        preauction.save()
    return render(request,'adminapprove.html',{'pending':pending_auction})    