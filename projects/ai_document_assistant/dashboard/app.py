import sys
from pathlib import Path

from dash import Dash, Input, Output, State, ctx, dcc, html


PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"
RAW_DIR = PROJECT_DIR / "data" / "raw"
VECTOR_STORE_DIR = PROJECT_DIR / "vector_store"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rag_pipeline import DocumentRagPipeline


external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

SUGGESTED_QUESTIONS = [
    "Rangkum profil kandidat",
    "Apa skill utama yang dimiliki?",
    "Apa pengalaman kerja terbaru?",
    "Apa project data science yang pernah dibuat?",
]

_pipeline = None


def get_document_count():
    return len(list(RAW_DIR.glob("*.pdf")))


def get_vector_store_status():
    return "Ready" if (VECTOR_STORE_DIR / "chroma.sqlite3").exists() else "Not built"


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = DocumentRagPipeline()
    return _pipeline


def render_sources(sources, mode):
    if not sources:
        return html.P("No source snippets available yet.", className="empty-text")

    source_type = "Direct page text" if mode == "page_lookup" else "Retrieved CV context"
    return [
        html.Div(
            className="source-item",
            children=[
                html.Div(
                    className="source-meta",
                    children=[
                        html.Span(f"Page {source.page}"),
                        html.Span(source_type),
                    ],
                ),
                html.P(source.text[:520].replace("\n", " ")),
            ],
        )
        for source in sources
    ]


app.layout = html.Div(
    className="dashboard-page",
    children=[
        html.Div(
            className="dashboard-header",
            children=[
                html.A("<- Back to Portfolio", href="http://127.0.0.1:8000/", className="back-btn"),
                html.P("RAG DOCUMENT ASSISTANT", className="eyebrow"),
                html.H1("AI Document Assistant"),
                html.P("Ask questions about the indexed CV documents and review the source evidence behind each answer."),
            ],
        ),
        html.Div(
            className="kpi-grid",
            children=[
                html.Div(className="kpi-card", children=[html.H3("Indexed PDFs"), html.P(str(get_document_count()))]),
                html.Div(className="kpi-card", children=[html.H3("Vector Store"), html.P(get_vector_store_status())]),
                html.Div(className="kpi-card", children=[html.H3("Chat Model"), html.P("GLM-5 Turbo")]),
                html.Div(className="kpi-card", children=[html.H3("Retrieval"), html.P("Top 2")]),
            ],
        ),
        html.Div(
            className="prediction-section",
            children=[
                html.Div(
                    className="prediction-header",
                    children=[
                        html.P("DOCUMENT Q&A", className="eyebrow"),
                        html.H2("Ask the Indexed Documents"),
                        html.P("Use a suggested question or write a custom question about the CV documents."),
                    ],
                ),
                html.Div(
                    className="assistant-shell",
                    children=[
                        html.Div(
                            className="question-panel",
                            children=[
                                html.Label("Question", htmlFor="question-input"),
                                dcc.Textarea(
                                    id="question-input",
                                    value="Rangkum profil kandidat",
                                    placeholder="Type a question about the CV documents...",
                                    className="question-input",
                                ),
                                html.Div(
                                    className="suggestion-row",
                                    children=[
                                        html.Button(
                                            question,
                                            id={"type": "suggestion-button", "index": index},
                                            n_clicks=0,
                                        )
                                        for index, question in enumerate(SUGGESTED_QUESTIONS)
                                    ],
                                ),
                                html.Button("Ask Document", id="ask-button", n_clicks=0, className="ask-button"),
                            ],
                        ),
                        html.Div(
                            className="answer-panel",
                            children=[
                                dcc.Loading(
                                    type="circle",
                                    color="#007c89",
                                    children=html.Div(
                                        id="answer-output",
                                        className="answer-output",
                                        children=[
                                            html.Div(className="status-pill", children="Ready"),
                                            html.H2("Answer will appear here"),
                                            html.P("Use a suggested question or type your own."),
                                        ],
                                    ),
                                )
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="chart-card sources-section",
            children=[
                html.Div(
                    className="section-heading",
                    children=[
                        html.P("EVIDENCE", className="eyebrow"),
                        html.H2("Source Snippets"),
                    ],
                ),
                html.Div(id="sources-output", className="sources-list"),
            ],
        ),
    ],
)


@app.callback(
    Output("question-input", "value"),
    Input({"type": "suggestion-button", "index": 0}, "n_clicks"),
    Input({"type": "suggestion-button", "index": 1}, "n_clicks"),
    Input({"type": "suggestion-button", "index": 2}, "n_clicks"),
    Input({"type": "suggestion-button", "index": 3}, "n_clicks"),
    State("question-input", "value"),
    prevent_initial_call=True,
)
def apply_suggestion(*values):
    current_question = values[-1]
    triggered = ctx.triggered_id
    if isinstance(triggered, dict):
        return SUGGESTED_QUESTIONS[triggered["index"]]
    return current_question


@app.callback(
    Output("answer-output", "children"),
    Output("sources-output", "children"),
    Input("ask-button", "n_clicks"),
    State("question-input", "value"),
    prevent_initial_call=True,
)
def answer_question(n_clicks, question):
    if not question or not question.strip():
        return (
            [
                html.Div(className="status-pill warning", children="Needs question"),
                html.H2("Type a question first"),
                html.P("The assistant needs a document question before it can search."),
            ],
            html.P("No source snippets available yet.", className="empty-text"),
        )

    try:
        result = get_pipeline().answer_question(question.strip())
    except Exception as exc:
        return (
            [
                html.Div(className="status-pill error", children="Error"),
                html.H2("Could not process the question"),
                html.P(str(exc)),
            ],
            html.P("Source snippets are unavailable because the process failed.", className="empty-text"),
        )

    mode_label = "Fast page lookup" if result.mode == "page_lookup" else "RAG answer"
    answer_children = [
        html.Div(className="status-pill", children=mode_label),
        html.H2("Answer"),
        html.P(result.answer),
    ]
    return answer_children, render_sources(result.sources, result.mode)


if __name__ == "__main__":
    app.run(debug=True, port=8052)
