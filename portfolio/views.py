from django.http import Http404
from django.shortcuts import render
from .models import Project
from . import dash_apps  # Register Dash apps

def home(request):
    featured_projects = Project.objects.all()[:3]
    return render(
        request,
        "portfolio/home.html",
        {"featured_projects": featured_projects},
    )

def about(request):
    return render(request, "portfolio/about.html")

def projects(request):
    projects_list = Project.objects.all().order_by("-created_at")
    return render(
        request,
        "portfolio/projects.html",
        {"projects": projects_list},
    )

def project_detail(request, slug):
    try:
        project = Project.objects.get(slug=slug)
    except Project.DoesNotExist:
        raise Http404("Project not found")

    return render(
        request,
        "portfolio/project_detail.html",
        {"project": project},
    )

def contact(request):
    return render(request, "portfolio/contact.html")

