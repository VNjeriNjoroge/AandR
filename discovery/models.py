from django.db import models

class Artist(models.Model):
    # --- Artist Identity ---
    name = models.CharField(max_length=255)
    # Storing IDs for multiple platforms to allow 360-degree tracking later
    youtube_channel_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    spotify_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    tiktok_handle = models.CharField(max_length=100, null=True, blank=True)
    profile_image_url = models.URLField(max_length=500, null=True, blank=True)
    
    # --- Classification ---
    genre = models.CharField(max_length=100, default="Afrobeats")
    is_unsigned = models.BooleanField(default=True) # Focus on independent talent
    location = models.CharField(max_length=100, default="Nigeria")
    is_blocked = models.BooleanField(default=False, help_text="Hide non-music/spam channels from the frontend")

    # --- Metrics (Snapshot for Velocity Calculation) ---
    current_subs = models.IntegerField(default=0)
    prev_subs = models.IntegerField(default=0)
    
    total_views = models.BigIntegerField(default=0)
    prev_views = models.BigIntegerField(default=0)
    
    current_comments = models.IntegerField(default=0)
    prev_comments = models.IntegerField(default=0)
    
    # --- TikTok Metrics ---
    tiktok_follower_count = models.IntegerField(default=0)
    prev_tiktok_follower_count = models.IntegerField(default=0)
    tiktok_likes = models.BigIntegerField(default=0)
    prev_tiktok_likes = models.BigIntegerField(default=0)
    discovered_on = models.CharField(max_length=50, default="youtube")
    
    # --- Metadata ---
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def growth_percentage(self):
        """Calculates the velocity of the artist's growth (Subs)."""
        if self.prev_subs <= 0:
            return 0
        return round(((self.current_subs - self.prev_subs) / self.prev_subs) * 100, 2)

    @property
    def view_growth_percentage(self):
        """Calculates the velocity of the artist's views."""
        if self.prev_views <= 0:
            return 0
        return round(((self.total_views - self.prev_views) / self.prev_views) * 100, 2)

    @property
    def tiktok_growth_percentage(self):
        if self.prev_tiktok_follower_count <= 0:
            return 0
        return round(((self.tiktok_follower_count - self.prev_tiktok_follower_count) / self.prev_tiktok_follower_count) * 100, 2)

    @property
    def tiktok_engagement_rate(self):
        if self.tiktok_follower_count <= 0:
            return 0
        return round((self.tiktok_likes / self.tiktok_follower_count) * 100, 2)

    @property
    def viral_potential_score(self):
        """Combined score based on subs, views, and estimated engagement."""
        # YouTube Score
        yt_score = (self.growth_percentage * 1.0) + (self.view_growth_percentage * 0.5)
        
        # TikTok Score
        tk_growth = self.tiktok_growth_percentage
        tk_like_growth = 0
        if self.prev_tiktok_likes > 0:
            tk_like_growth = (((self.tiktok_likes - self.prev_tiktok_likes) / self.prev_tiktok_likes) * 100)
        tk_score = (tk_growth * 1.5) + (tk_like_growth * 0.5)
        
        return round(max(yt_score, tk_score), 1)

    @property
    def viral_label(self):
        """Categorizes viral potential."""
        score = self.viral_potential_score
        if score >= 15.0: return "High"
        if score >= 5.0: return "Medium"
        return "Low"

    @property
    def viral_status(self):
        """Legacy status, keeping for compatibility but updating logic."""
        if self.viral_label == "High": return "🔥 Viral"
        if self.viral_label == "Medium": return "📈 Rising"
        return "💎 Emerging"

    def __str__(self):
        return f"{self.name} ({self.genre})"
