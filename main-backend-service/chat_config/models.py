from django.db import models
import uuid

# Create your models here.
class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default=uuid.uuid4)
<<<<<<< HEAD
    user_id = models.IntegerField()  
    dataset = models.URLField(max_length=5000)
=======
    user_id = models.CharField(max_length=255, default=uuid.uuid4)  
    dataset = models.CharField(max_length=5000)
>>>>>>> c182dc6 (single api for crate chat and upload data)
    name_generated = models.BooleanField(default=False)  # ✅ Changed to Boolean
    created_At = models.DateTimeField(auto_now_add=True)
    
    
    SOURCE_TYPE_CHOICES = [
        ("file", "File"),
        ("database_url", "Database URL"),
    ]
    
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default="file"
    )
    def __str__(self):
        return self.name
    
