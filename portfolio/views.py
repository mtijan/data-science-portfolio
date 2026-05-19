from django.http import Http404
from django.shortcuts import render


PROJECTS = [
    {
        "slug": "sales-dashboard",
        "title": "Sales Performance Dashboard",
        "category": "Business Intelligence",
        "summary": "Interactive dashboard to monitor revenue, product performance, and customer trends.",
        "tools": ["Python", "pandas", "Dash", "Plotly"],
        "problem": "Business teams need a clear view of sales performance across time, products, and customer segments.",
        "approach": "Build an interactive dashboard with KPI cards, trend charts, and filters for exploratory analysis.",
        "result": "Decision makers can quickly identify revenue growth, weak product categories, and potential sales opportunities.",
        "status": "Planned",
        "demo_url": "http://127.0.0.1:8050/",
        "repo_url": "https://github.com/mtijan/data-science-portfolio",
    },
    {
        "slug": "churn-prediction",
        "title": "Customer Churn Prediction",
        "category": "Machine Learning",
        "summary": "Classification model to identify customers with high churn risk.",
        "tools": ["Python", "pandas", "scikit-learn", "FastAPI"],
        "problem": "Companies often lose customers without early warning signals.",
        "approach": "Train a classification model using customer behavior data and expose predictions through an API.",
        "result": "The model helps prioritize retention campaigns for customers with the highest churn probability.",
        "status": "Planned",
        "demo_url": "#",
        "repo_url": "https://github.com/mtijan/data-science-portfolio",
    },
    {
        "slug": "ai-document-assistant",
        "title": "AI Document Assistant",
        "category": "GenAI / RAG",
        "summary": "Document Q&A assistant for retrieving answers from PDFs and business reports.",
        "tools": ["Python", "LangChain", "Vector Database", "LLM"],
        "problem": "Important business information is often buried inside long documents.",
        "approach": "Use embeddings and retrieval augmented generation to answer questions from uploaded documents.",
        "result": "Users can ask natural language questions and receive grounded answers from source documents.",
        "status": "Planned",
        "demo_url": "#",
        "repo_url": "https://github.com/mtijan/data-science-portfolio",
    },
]


def home(request):
    featured_projects = PROJECTS[:3]
    return render(
        request,
        "portfolio/home.html",
        {"featured_projects": featured_projects},
    )


def about(request):
    return render(request, "portfolio/about.html")


def projects(request):
    return render(
        request,
        "portfolio/projects.html",
        {"projects": PROJECTS},
    )


def project_detail(request, slug):
    project = next((item for item in PROJECTS if item["slug"] == slug), None)

    if project is None:
        raise Http404("Project not found")

    return render(
        request,
        "portfolio/project_detail.html",
        {"project": project},
    )


def contact(request):
    return render(request, "portfolio/contact.html")

