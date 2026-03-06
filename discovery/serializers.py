from rest_framework import serializers
from .models import Artist

class ArtistSerializer(serializers.ModelSerializer):
    # We explicitly include our custom properties from the model
    growth = serializers.ReadOnlyField(source='growth_percentage')
    status = serializers.ReadOnlyField(source='viral_status')
    viral_label = serializers.ReadOnlyField()
    viral_score = serializers.ReadOnlyField(source='viral_potential_score')
    tiktok_growth = serializers.ReadOnlyField(source='tiktok_growth_percentage')
    engagement = serializers.ReadOnlyField(source='tiktok_engagement_rate')

    class Meta:
        model = Artist
        fields = [
            'id', 'name', 'genre', 'current_subs', 'total_views', 'growth', 'status', 'location', 
            'youtube_channel_id', 'profile_image_url', 'viral_label', 'viral_score',
            'tiktok_handle', 'tiktok_follower_count', 'tiktok_likes', 'discovered_on',
            'tiktok_growth', 'engagement'
        ]