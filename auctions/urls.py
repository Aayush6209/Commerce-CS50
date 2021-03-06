from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createListing", views.createListing, name="createListing"),
    path("<int:listing_id>/listing", views.listing, name="listing"),
    path("<int:listing_id>/Addcomment", views.Addcomment, name="Addcomment"),
    path("categories", views.categories, name="categories"),
    path("watchlist", views.watchlist, name="watchlist")
]
