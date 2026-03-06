from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Artist
from .serializers import ArtistSerializer

class DiscoveryDashboard(APIView):
    def get(self, request):
        platform = request.query_params.get('platform', 'youtube').lower()
        
        # Target: Emerging talent (< 5000 followers/subs)
        if platform == 'tiktok':
            artists = Artist.objects.filter(is_blocked=False, tiktok_handle__isnull=False, tiktok_follower_count__lt=5000)
        else:
            artists = Artist.objects.filter(is_blocked=False, youtube_channel_id__isnull=False, current_subs__lt=5000)

        # We sort in Python because growth_percentage is a @property
        sorted_artists = sorted(
            artists, 
            key=lambda x: x.viral_potential_score, 
            reverse=True
        )
        
        serializer = ArtistSerializer(sorted_artists, many=True)
        return Response(serializer.data)
