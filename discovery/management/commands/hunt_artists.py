from django.core.management.base import BaseCommand
from discovery.services import sync_rising_artists, hunt_for_new_nigerian_artists, hunt_tiktok_rising_stars

class Command(BaseCommand):
    help = 'Fetches new Nigerian artists from YouTube and TikTok and updates metrics'

    def handle(self, *args, **kwargs):
        self.stdout.write("🔎 Initiating hunt for new artists on YouTube...")
        hunt_for_new_nigerian_artists()
        
        self.stdout.write("🎵 Initiating hunt for new artists on TikTok...")
        hunt_tiktok_rising_stars()
        
        self.stdout.write("📊 Syncing growth metrics for YouTube...")
        sync_rising_artists()
        
        self.stdout.write(self.style.SUCCESS('✅ Hunt complete! Database updated.'))
