from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import related


class User(AbstractUser):
    pass


class Auction(models.Model):
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="auctions", default=None)
    title = models.CharField(max_length=64)
    description = models.TextField()
    current_price = models.FloatField()
    photo = models.URLField()
    startingPrice = models.FloatField()
    date = models.DateField()
    time = models.TimeField()
    cat = models.CharField(max_length=64)
    watchList = models.ManyToManyField(
        User, blank=True, related_name="full_list")
    winner = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="won_auction", default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.title}, {self.current_price}"

    def getWinner(self):
        return self.winner


class Comment(models.Model):
    product = models.ForeignKey(
        Auction, on_delete=models.CASCADE, related_name="comments", default=None)
    commentator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments", default=None)
    comment = models.TextField(default=None)

    def __str__(self):
        return f"{self.commentator}: {self.comment}"


class Bid(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="buyer", default=None)
    auction = models.ForeignKey(
        Auction, on_delete=models.CASCADE, related_name="auctionBid", default=None)
    bidAmt = models.IntegerField(default=None)

    def __str__(self):
        return f"Bid no. {self.id}: ${self.bidAmt}"

    def getBid(self):
        return self.bidAmt

    def getUser(self):
        return self.customer

    def getAuction(self):
        return self.auction
