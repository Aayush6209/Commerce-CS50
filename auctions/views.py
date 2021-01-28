import auctions
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, response
from django.shortcuts import redirect, render
from django.urls import reverse

import datetime

from .models import User, Auction, Bid, Comment


# category = ["Automobile", "Electronics",
#             "House holds", "Books", "Clothes", "Others"]


def index(request):

    # auctions returns all the current auctions present on database

    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.all()
    })


# PRE-implimented
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")



# PRE-implimented
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))



# PRE-implimented
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing(request, listing_id):

    # if user clicks on picture then check if he is logged in or not
    if not request.user.is_authenticated:
        return login_view(request)

    if request.method == "POST":
        # if owner closed the auction
        if request.POST.get("CLOSE", None) is not None:

            listing = Auction.objects.get(pk=listing_id)
            bids = Bid.objects.filter(auction=listing)

            # finding the winner
            winner = None
            max_bid = None
            for bid in bids:
                if (max_bid is None or max_bid < int(bid.getBid())):
                    max_bid = int(bid.getBid())
                    winner = bid.getUser()
            
            # updating the winner field from None to <winner>
            listing.winner = winner
            listing.save()

            return render(request, "auctions/index.html", {
                "auctions": Auction.objects.all(),
                "message": "Auction completed!"
            })

        # new Bid being placed
        product = Auction.objects.get(pk=int(request.POST["product"]))
        price_placed = float(request.POST["amt"])

        # if current bid is larger
        if product.current_price < price_placed:
            product.current_price = price_placed
            product.save()

            # if Bid was placed by same buyer then update it
            try:
                bid = Bid.objects.get(pk=int(request.POST["buyer"]))
                bid.bidAmt = price_placed
                bid.save()

            # else make new bid
            except:
                Newbid = Bid(auction=Auction.objects.get(pk=int(request.POST["product"])),
                             bidAmt=price_placed,
                             customer=User.objects.get(pk=request.POST["buyer"]))
                Newbid.save()

            return render(request, "auctions/index.html", {
                "auctions": Auction.objects.all(),
                "message": "Bid Placed successfully"
            })

        # if amount was less than current amount
        else:
            return render(request, "auctions/index.html", {
                "auctions": Auction.objects.all(),
                "lessAmt": "Bidding amount is less"
            })

    # if a user just clicks on a listing
    user = User.objects.get(username=request.user.username)
    listing = Auction.objects.get(pk=listing_id)
    seller = Auction.objects.get(pk=listing_id).seller
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bidCount": Bid.objects.filter(auction=listing_id).count(),
        "seller": seller,
        "comments": Comment.objects.filter(product=listing_id),
        "commentCount": Comment.objects.filter(product=listing_id).count(),
        "Present_already": True if listing in user.full_list.all() else False,
        "Creator": True if user == seller else False,
        "winner": listing.getWinner()
    })


def createListing(request):
    
    # creating a new listing
    if request.method == "POST":
        seller = User.objects.get(pk=int(request.POST["seller"]))
        title = request.POST["title"]
        description = request.POST["description"]
        startBid = request.POST["bid"]
        category = str(request.POST["category"])
        photo = request.POST["image"]
        auction = Auction(seller=seller, title=title, description=description,
                          current_price=float(startBid),
                          startingPrice=float(startBid),
                          photo=photo,
                          date=datetime.datetime.now().date(),
                          time=datetime.datetime.now().time(),
                          cat=category)
        auction.save()
        return index(request)
    
    # if create listing link is pressed by user: render the create listing page
    else:
        return render(request, "auctions/createListing.html", {
            "categories": ["Automobile", "Electronics", "Home", "Books", "Fashion", "Toys", "Others"]
        })


def Addcomment(request, listing_id):
    if request.method == "POST":
        # if user comments then check if he is logged in or not
        if not request.user.is_authenticated:
            return login_view(request)
        listing = Auction.objects.get(pk=listing_id)
        commentator = User.objects.get(username=request.POST["commentator"])
        comment = request.POST["comment"]
        newComment = Comment(
            product=listing, commentator=commentator, comment=comment)
        newComment.save()
    return index(request)


def categories(request):
    
    # when a user posts his category type give him all products with that category
    if request.method == "POST":
        category = request.POST["category"]
        # cat stands for category in Auction table
        auctions = Auction.objects.filter(cat=category)
        return render(request, "auctions/index.html", {
            "auctions": auctions
        })

    # when a user clicks on category link on layout.html
    else:
        return render(request, "auctions/categories.html", {
            "categories": ["Automobile", "Electronics", "Home", "Books", "Fashion", "Toys", "Others"]
        })


def watchlist(request):
    user = User.objects.get(username=request.user.username)
    if request.method == "POST":
        Listing = Auction.objects.get(pk=request.POST["listing"])
        if request.POST.get("remove", None) is None:
            Listing.watchList.add(user)
        else:
            Listing.watchList.remove(user)
        return HttpResponseRedirect(reverse("listing", args=(Listing.id,)))
    else:
        return render(request, "auctions/watchlist.html", {
            "Wlist": user.full_list.all()
        })


# vaccum: https://www.thespruce.com/thmb/P2TnzY6IErrYCIlzRo9ABOFGnSk=/960x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/GettyImages-985640624-5c716102cff47e0001b1e319.jpg

# car: https://imgd.aeplcdn.com/1056x594/cw/ec/26916/Audi-Q3-Front-view-92293.jpg?v=201711021421&q=85

# t-shirt: https://5.imimg.com/data5/VT/DS/MY-17368652/plain-round-neck-tshirt-500x500.jpg

# toy: https://rukminim1.flixcart.com/image/704/704/k547l3k0/stuffed-toy/2/b/5/valentine-gift-pink-teddy-bear-soft-toy-22-agnolia-original-imaffzzp3asyjywe.jpeg?q=70

# sofa: https://5.imimg.com/data5/CO/EU/NR/SELLER-2026855/sofa-set-500x500.jpg

# flower: https://images-na.ssl-images-amazon.com/images/I/71CuXqhULOL._SL1500_.jpg
