from django.http import Http404
from django.shortcuts import render


PROJECTS = [
    {
        "slug": "sales-dashboard",
        "title": "Sales Performance Dashboard",
        "category": "Business Intelligence",
        "summary": "Interactive dashboard to monitor revenue, product performance, and customer trends.",
        "tools": ["Python", "pandas", "Dash", "Plotly"],
        "problem": "Business teams need a clear view of sales performance across revenue, profit, products, regions, and customer segments.",
        "approach": "Cleaned raw e-commerce data, engineered time-based business metrics, and built an interactive dashboard with KPI cards, filters, and Plotly charts.",
        "result": "Built a dashboard covering $484K sales, $158K profit, 2,000 orders, and product, region, customer, and discount performance insights.",
        "business_impact": "Helps business teams monitor revenue trends, identify top products, evaluate discount impact, and prioritize profitable regions.",
        "status": "Completed",
        "demo_url": "http://127.0.0.1:8050/",
        "repo_url": "https://github.com/mtijan/data-science-portfolio",
    },
    {
        "slug": "churn-prediction",
        "title": "Customer Churn Prediction",
        "category": "Machine Learning",
        "summary": "Classification model to identify customers with high churn risk and support retention campaigns.",
        "tools": ["Python", "pandas", "scikit-learn", "matplotlib", "seaborn"],
        "problem": "Customer churn reduces recurring revenue and increases acquisition costs, so business teams need a way to identify at-risk customers before they leave.",
        "approach": "Cleaned Telco customer data, engineered billing and contract features, compared multiple classification models, and tuned the decision threshold for churn detection.",
        "result": "Built a Gradient Boosting churn model with 0.8435 ROC-AUC and 78.88% churn recall at the selected threshold.",
        "business_impact": "Helps retention teams prioritize high-risk customers, especially month-to-month customers with short tenure, high monthly charges, and electronic check payment.",
        "status": "In Progress",
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

