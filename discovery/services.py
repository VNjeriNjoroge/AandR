import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()
from .models import Artist

def sync_rising_artists():
    """
    Fetches latest stats for all artists in the DB.
    Optimized to update up to 50 artists in a single API call.
    """
    # 1. Initialize API
    api_key = os.getenv("YOUTUBE_API_KEY")
    youtube = build('youtube', 'v3', developerKey=api_key, static_discovery=False)

    # 2. Get all artists with a YouTube ID
    artists = Artist.objects.exclude(youtube_channel_id__isnull=True).filter(is_blocked=False)
    if not artists.exists():
        print("No artists found in database.")
        return

    # 3. Batch process IDs (YouTube API allows up to 50 at once)
    ids = [a.youtube_channel_id for a in artists]
    
    for i in range(0, len(ids), 50):
        batch_ids = ids[i:i+50]
        try:
            request = youtube.channels().list(
                part='statistics,snippet',
                id=",".join(batch_ids)
            )
            response = request.execute()

            # 4. Update each artist in our DB
            for item in response.get('items', []):
                channel_id = item['id']
                stats = item['statistics']
                snippet = item['snippet'] # Get snippet for thumbnails
                
                artist = Artist.objects.get(youtube_channel_id=channel_id)
                
                # Filter non-Nigerian and "Topic" channels
                country = snippet.get('country')
                if country and country != 'NG':
                    print(f"Skipping & removing non-Nigerian artist: {artist.name} (Country: {country})")
                    artist.delete()
                    continue
                    
                if "topic" in artist.name.lower() or "vevo" in artist.name.lower() or "tv" in artist.name.lower() or "records" in artist.name.lower():
                    print(f"Skipping & removing Brand/Topic channel: {artist.name}")
                    artist.delete()
                    continue
                
                # Save current counts to 'prev' before updating
                # DEMO MODE: If prev_subs/prev_views are 0, initialize them to show growth immediately
                stats_subs = int(stats.get('subscriberCount', 0))
                stats_views = int(stats.get('viewCount', 0))
                stats_video_count = int(stats.get('videoCount', 0))
                
                # --- SUBSCRIBER GROWTH ---
                if artist.prev_subs == 0 and stats_subs > 0:
                    import random
                    reduction_factor = random.uniform(0.85, 0.98)
                    artist.prev_subs = int(stats_subs * reduction_factor)
                elif artist.current_subs > 0:
                    artist.prev_subs = artist.current_subs # Normal update
                
                # --- VIEW GROWTH ---
                if artist.prev_views == 0 and stats_views > 0:
                    import random
                    # Views fluctuate more than subs
                    reduction_factor = random.uniform(0.90, 0.99)
                    artist.prev_views = int(stats_views * reduction_factor)
                elif artist.total_views > 0:
                    artist.prev_views = artist.total_views # Normal update

                # --- COMMENT/ENGAGEMENT ESTIMATION ---
                # API doesn't give total comments easily. We estimate based on views or video count if not available.
                # Ideally we would fetch videos, but keeping quota low for now.
                artist.prev_comments = artist.current_comments
                # Estimate: 0.5% engagement rate on views (generic heuristic for MVP)
                artist.current_comments = int(stats_views * 0.005) 
                
                # Update latest stats
                artist.current_subs = stats_subs
                artist.total_views = stats_views
                
                # Update profile image
                if 'thumbnails' in snippet:
                    # Try high, then medium, then default
                    thumbnails = snippet['thumbnails']
                    if 'high' in thumbnails:
                        artist.profile_image_url = thumbnails['high']['url']
                    elif 'medium' in thumbnails:
                         artist.profile_image_url = thumbnails['medium']['url']
                    else:
                        artist.profile_image_url = thumbnails['default']['url']
                
                artist.save()
                print(f"Updated: {artist.name} | Growth: {artist.growth_percentage}%")

        except Exception as e:
            print(f"Error syncing batch with YouTube: {e}")

def hunt_for_new_nigerian_artists():
    """Searches YouTube for new Nigerian artists and adds them to the DB."""
    api_key = os.getenv("YOUTUBE_API_KEY")
    youtube = build('youtube', 'v3', developerKey=api_key, static_discovery=False)

    # Keywords to find the "next big thing" in Nigeria
    search_queries = [
        "Afrobeats emerging artist 2026", 
        "New Nigerian Music 2026", 
        "Rising Afrobeats",
        "Naija street pop upcoming",
        "Upcoming artists Nigeria",
        "Next rated Nigeria 2026"
    ]

    for query in search_queries:
        next_page_token = None
        for _ in range(2): # 2 pages per query, max 50 items = 100 channels per query (600 max raw)
            request = youtube.search().list(
                q=query,
                type="channel",
                part="snippet",
                maxResults=50,
                regionCode="NG", # Focus on Nigeria
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response.get('items', []):
                channel_id = item['snippet']['channelId']
                channel_title = item['snippet']['title']

                if "topic" in channel_title.lower() or "vevo" in channel_title.lower() or "tv" in channel_title.lower() or "records" in channel_title.lower():
                    continue

                # Only add them if they aren't in our database yet
                Artist.objects.get_or_create(
                    youtube_channel_id=channel_id,
                    defaults={'name': channel_title, 'genre': 'Afrobeats', 'discovered_on': 'youtube'}
                )
                print(f"Discovered & Added: {channel_title}")
                
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

def hunt_tiktok_rising_stars():
    """
    Simulates scraping TikTok for emerging artists with < 5000 followers.
    In a real scenario, this would use Apify or EnsembleData API.
    """
    import random
    
    print("🥁 Scraping TikTok for #Afrobeats hidden gems...")
    
    mock_tiktok_handles = [
        "@afro_kid_music", "@naija_vibe_king", "@bella_beats_ng",
        "@dope_szn_afro", "@lagos_soundz", "@new_wave_afro",
        "@tems_soundalike", "@rema_vibes_26", "@underground_afro"
    ]
    
    for handle in mock_tiktok_handles:
        # Simulate stats: Followers between 100 - 4500
        followers = random.randint(100, 4500)
        # Previous followers to simulate growth velocity (very high for TikTok)
        prev_followers = int(followers * random.uniform(0.3, 0.8)) # Great jumps!
        
        # simulated Engagement > 5% 
        likes = followers * random.randint(10, 50) 
        prev_likes = int(likes * random.uniform(0.4, 0.9))
        
        artist, created = Artist.objects.get_or_create(
            tiktok_handle=handle,
            defaults={
                'name': handle.strip('@').replace('_', ' ').title(),
                'genre': 'Afrobeats',
                'discovered_on': 'tiktok',
                'tiktok_follower_count': followers,
                'prev_tiktok_follower_count': prev_followers,
                'tiktok_likes': likes,
                'prev_tiktok_likes': prev_likes,
                'is_blocked': False,
            }
        )
        
        if not created:
            # Update existing if already discovered
            artist.prev_tiktok_follower_count = artist.tiktok_follower_count
            artist.tiktok_follower_count = followers
            
            artist.prev_tiktok_likes = artist.tiktok_likes
            artist.tiktok_likes = likes
            artist.save()
            print(f"Updated TikTok stats: {handle}")
        else:
            print(f"Discovered & Added on TikTok: {handle} ({followers} followers)")