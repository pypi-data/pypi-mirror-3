class Status(models.Model):
    tweet = models.CharField(max_length=250)
    twitter_id = models.BigIntegerField()
    created_at = models.CharField(max_length=200)
    location = models.ForeignKey(Location)
    
    def __unicode__(self):
        return self.tweet
    
    class Meta:
        ordering = ['-twitter_id']