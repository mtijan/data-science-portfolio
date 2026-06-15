from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=100)
    summary = models.TextField()
    tools = models.JSONField(default=list)
    problem = models.TextField()
    approach = models.TextField()
    result = models.TextField()
    business_impact = models.TextField()
    status = models.CharField(max_length=50, default="In Progress")
    demo_url = models.URLField(blank=True, null=True)
    repo_url = models.URLField(blank=True, null=True)
    dash_app_name = models.CharField(max_length=100, blank=True, null=True)
    features = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
