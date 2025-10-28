from django.db import models

from chat_config.models import Chat

class Prompt(models.Model):
    prompt = models.TextField() 
    result_txt = models.TextField(blank=True, null=True)  
    result_img = models.URLField(max_length=1000, blank=True, null=True)
    
    chat_id = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        db_column='chat_id',      
        related_name='prompts'    
    )
    generated_code = models.TextField()
    
    def __str__(self):
        return f"Prompt {self.id} - {self.prompt[:50]}"
