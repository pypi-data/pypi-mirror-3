

**Update your models**

Django uses a custom Profile model to store additional user information. Read more about this topic in the https://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users Django Docs.
If you don't already have a custom Profile model, simply uses the provided model by setting your AUTH_PROFILE_MODULE to FacebookProfile:

::
  
    AUTH_PROFILE_MODULE == 'django_facebook.FacebookProfile'

Otherwise Django Facebook provides an abstract model which you can inherit like this:

::
    from django_facebook.models import FacebookProfileModel


    class MyCustomProfile(FacebookProfileModel):
        user = models.OneToOneField('auth.User')
        ....
    
    from django.contrib.auth.models import User
    from django.db.models.signals import post_save
    
    #Make sure we create a MyCustomProfile when creating a User
    def create_facebook_profile(sender, instance, created, **kwargs):
        if created:
            MyCustomProfile.objects.create(user=instance)
    
    post_save.connect(create_facebook_profile, sender=User)
    
    
    