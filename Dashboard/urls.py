from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path("AuctionItem/<int:auction_id>", views.AuctionItem, name="AuctionItem"),
    path("AuctionItem/<int:auction_id>/comment", views.comment, name="comment"),
    path('create_auction/', views.create_auction, name='create_auction'),
    path("Live_Auction/", views.LiveAuction, name="LiveAuction"),
    path("Upcoming_Auction/", views.UpcomingAuction, name="UpcomingAuction"),
    path("Admin_approve/", views.adminapprove, name="adminapprove"),
    path("AuctionItem/<int:auction_id>/bid_placement", views.bitplacement, name="bitplacement"),
    path('AuctionItem/<int:auction_id>/load_bids/', views.load_bids, name='load_bids'),
    path('search/', views.search_auctions, name='search_auctions'),
    path('Advanced_search/', views.advanced_search_properties, name='advanced_search_properties'),
    path('watchlist/', views.view_watchlist, name='view_watchlist'),
    
]