from django.db import models
import re

class Video(models.Model):
    title = models.CharField(max_length=255)
    src = models.URLField(max_length=200)
    thumbnail = models.URLField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        # Extract YouTube video ID from the src URL
        youtube_id = self.extract_youtube_id(self.src)
        if youtube_id:
            self.thumbnail = f"https://img.youtube.com/vi/{youtube_id}/0.jpg"
        super().save(*args, **kwargs)

    @staticmethod
    def extract_youtube_id(url):
        """
        Extract the YouTube video ID from the URL.
        Example: https://www.youtube.com/watch?v=HG3hB8PE2f8 -> HG3hB8PE2f8
        """
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def __str__(self):
        return self.title
