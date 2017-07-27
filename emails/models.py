from django.db import models


class EmailSignup(models.Model):
    email_address = models.EmailField(blank=False, null=False, unique=True)
    signup_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email_address
