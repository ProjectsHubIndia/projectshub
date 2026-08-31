"""
Management command to seed the database with sample data.
Run with: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from core.models import (
    Project, ProjectHighlight, ProjectTimelinePhase, ProjectFeature,
    WorkshopCard, WorkshopDay,
    PricingPlan, PricingFeature
)


class Command(BaseCommand):
    help = 'Seed the database with sample projects, workshops and pricing plans'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        self._seed_projects()
        self._seed_workshops()
        self._seed_pricing()
        self.stdout.write(self.style.SUCCESS('OK Database seeded successfully!'))

    # ── Projects ──────────────────────────────────────────────────────────────

    def _seed_projects(self):
        projects = [
            {
                'title': 'AI Sentiment Analyser',
                'description': 'Real-time sentiment analysis of customer reviews using fine-tuned BERT with a FastAPI backend and React dashboard processing 100K+ reviews daily.',
                'detailed_description': (
                    'This project implements a production-ready NLP sentiment analysis pipeline. '
                    'A domain-fine-tuned BERT-base model classifies customer reviews as positive, negative, or neutral '
                    'with 94% accuracy. The async FastAPI backend handles both single-text and batch inference, '
                    'while Redis queuing smooths out traffic spikes. The React dashboard visualises sentiment trends '
                    'over time with interactive filters by product, date range, and confidence score.\n\n'
                    'The biggest engineering challenge was latency — naive BERT inference was 350ms per request. '
                    'By switching to ONNX Runtime with 8-bit quantisation and implementing intelligent request '
                    'batching, average latency dropped to under 80ms while GPU memory usage fell by 40%. '
                    'The result is a system that can handle bursts of 500+ concurrent users without degradation.'
                ),
                'subtitle': 'Production-grade NLP pipeline processing 100K+ customer reviews daily at sub-80ms latency.',
                'year': '2025',
                'role': 'ML Engineer',
                'duration': '3 Months',
                'team_size': 'Solo Project',
                'tags': 'PyTorch, BERT, FastAPI, React, Docker, Redis, ONNX',
                'category': 'ml',
                'image_url': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&auto=format&fit=crop',
                'show_on_index': True,
                'order': 1,
                'highlights': [
                    {'icon': 'chart', 'value': '94.2%', 'label': 'Accuracy'},
                    {'icon': 'clock', 'value': '<80ms', 'label': 'Avg Latency'},
                    {'icon': 'users', 'value': '100K+', 'label': 'Daily Reviews'},
                    {'icon': 'star', 'value': '4.8★', 'label': 'Client Rating'},
                ],
                'detail_images': [
                    {
                        'url': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&auto=format&fit=crop',
                        'alt': 'Sentiment Dashboard Overview',
                        'caption': 'Real-time Sentiment Dashboard',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop',
                        'alt': 'Analytics & Trend Charts',
                        'caption': 'Sentiment Trend Analytics',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&auto=format&fit=crop',
                        'alt': 'FastAPI Swagger Interface',
                        'caption': 'FastAPI Inference API (Swagger UI)',
                    },
                ],
                'diagrams': [
                    {
                        'url': 'https://images.unsplash.com/photo-1607705703571-c5a8695f18f6?w=800&auto=format&fit=crop',
                        'label': 'Architecture',
                        'title': 'System Architecture Diagram',
                        'desc': 'BERT → ONNX Runtime → FastAPI → Redis queue → React dashboard end-to-end flow.',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800&auto=format&fit=crop',
                        'label': 'Data Flow',
                        'title': 'Inference Pipeline Flow',
                        'desc': 'How raw review text is pre-processed, tokenised, batched, and scored in real time.',
                    },
                ],
                'timeline_phases': [
                    {
                        'phase': 'Phase 01', 'date': 'Aug 2025',
                        'title': 'Data Collection & EDA',
                        'desc': 'Scraped and cleaned 500K customer reviews across e-commerce domains. Conducted EDA on class distribution, text length, and domain vocabulary shift.',
                    },
                    {
                        'phase': 'Phase 02', 'date': 'Sep 2025',
                        'title': 'Model Fine-tuning & Optimisation',
                        'desc': 'Fine-tuned BERT-base on domain data, compared DistilBERT and RoBERTa, then applied ONNX quantisation to cut latency from 350ms to 80ms.',
                    },
                    {
                        'phase': 'Phase 03', 'date': 'Oct 2025',
                        'title': 'API & Dashboard Build',
                        'desc': 'Built async FastAPI server with batch queuing and Redis caching. Built React dashboard with live sentiment charts, product filters, and CSV export.',
                    },
                    {
                        'phase': 'Phase 04', 'date': 'Nov 2025',
                        'title': 'Deployment & Monitoring',
                        'desc': 'Dockerised and deployed on AWS ECS Fargate. Set up CloudWatch alarms, load-tested to 500 concurrent users, and implemented automated rollbacks.',
                    },
                ],
                'github_url': 'https://github.com/ProjectsHub/ai-sentiment-analyser',
                'project_url': '',
                'price': 2999,
                'price_label': '₹2,999',
                'price_features': [
                    'Complete source code (FastAPI + React frontend)',
                    'Fine-tuned BERT model weights (ONNX format)',
                    'Docker Compose for local development',
                    'AWS ECS Fargate deployment guide (PDF)',
                    '60-minute video walkthrough',
                    '30-day email support',
                ],
            },
            {
                'title': 'Stock Price Predictor',
                'description': 'LSTM-based time-series forecasting model with Monte Carlo dropout confidence bands, deployed serverlessly on AWS Lambda for under 200ms predictions.',
                'detailed_description': (
                    'A multi-layer LSTM architecture trained on 10 years of historical OHLCV data for 50+ equities. '
                    'Technical indicators — RSI, MACD, Bollinger Bands, OBV — are engineered as additional features. '
                    'Walk-forward validation prevents look-ahead bias, and Monte Carlo Dropout generates uncertainty '
                    'quantification bands around each forecast. The entire model is packaged as an AWS Lambda function '
                    'with a DynamoDB cache layer to serve repeat queries instantly.\n\n'
                    'The core challenge was keeping inference cold-start under 3 seconds while running a 4-layer LSTM '
                    'on Lambda. This was solved by serialising the model to TorchScript, stripping unused weights, '
                    'and using Lambda SnapStart. Cache hit rate on repeat tickers reached 78%, dropping average '
                    'end-to-end latency below 200ms.'
                ),
                'subtitle': 'LSTM forecasting with Monte Carlo uncertainty bands, served serverlessly under 200ms.',
                'year': '2025',
                'role': 'ML Engineer',
                'duration': '2 Months',
                'team_size': 'Solo Project',
                'tags': 'TensorFlow, LSTM, AWS Lambda, DynamoDB, yfinance, TorchScript',
                'category': 'ml',
                'image_url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop',
                'show_on_index': True,
                'order': 2,
                'highlights': [
                    {'icon': 'chart', 'value': '87.3%', 'label': 'Direction Accuracy'},
                    {'icon': 'clock', 'value': '<200ms', 'label': 'Serverless Latency'},
                    {'icon': 'users', 'value': '10yr', 'label': 'Training Data'},
                    {'icon': 'star', 'value': '4.7★', 'label': 'User Rating'},
                ],
                'detail_images': [
                    {
                        'url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&auto=format&fit=crop',
                        'alt': 'Forecast Chart',
                        'caption': 'Forecasted vs Actual Price with Confidence Bands',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&auto=format&fit=crop',
                        'alt': 'Technical Indicators Dashboard',
                        'caption': 'Technical Indicator Feature Dashboard',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop',
                        'alt': 'Model Evaluation Metrics',
                        'caption': 'Walk-forward Validation Evaluation Report',
                    },
                ],
                'diagrams': [
                    {
                        'url': 'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800&auto=format&fit=crop',
                        'label': 'Architecture',
                        'title': 'Serverless Inference Architecture',
                        'desc': 'yfinance data → feature engineering → TorchScript LSTM → Lambda → DynamoDB cache → REST API.',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&auto=format&fit=crop',
                        'label': 'Model Design',
                        'title': 'LSTM Architecture & Training Flow',
                        'desc': 'Walk-forward split strategy, Monte Carlo Dropout uncertainty quantification, and hyperparameter tuning pipeline.',
                    },
                ],
                'timeline_phases': [
                    {
                        'phase': 'Phase 01', 'date': 'Sep 2025',
                        'title': 'Data Engineering & Feature Design',
                        'desc': 'Fetched 10 years of OHLCV data via yfinance for 50 equities. Engineered 22 technical indicators and normalised with rolling z-score to prevent leakage.',
                    },
                    {
                        'phase': 'Phase 02', 'date': 'Oct 2025',
                        'title': 'Model Training & Validation',
                        'desc': 'Built 4-layer LSTM with dropout, ran walk-forward cross-validation, and implemented Monte Carlo Dropout for prediction intervals.',
                    },
                    {
                        'phase': 'Phase 03', 'date': 'Oct 2025',
                        'title': 'Serverless Packaging',
                        'desc': 'Converted model to TorchScript, stripped unused weights, and packaged for AWS Lambda. Implemented DynamoDB caching layer to serve repeat tickers instantly.',
                    },
                    {
                        'phase': 'Phase 04', 'date': 'Nov 2025',
                        'title': 'API & Monitoring',
                        'desc': 'Built REST API with API Gateway, added CloudWatch dashboards for latency and cache-hit tracking, and load-tested to 100 concurrent users.',
                    },
                ],
                'github_url': 'https://github.com/ProjectsHub/stock-price-predictor',
                'project_url': '',
                'price': 3999,
                'price_label': '₹3,999',
                'price_features': [
                    'Full source code (training + Lambda function)',
                    'Pre-trained TorchScript model weights',
                    'AWS Lambda + API Gateway deployment template (SAM)',
                    'Feature engineering notebook with explanations',
                    '45-minute video walkthrough',
                    '30-day email support',
                ],
            },
            {
                'title': 'Customer Churn Pipeline',
                'description': 'End-to-end MLOps pipeline for churn prediction with automated retraining, data drift detection, and Grafana monitoring — built on MLflow, Prefect, and XGBoost.',
                'detailed_description': (
                    'An enterprise-grade MLOps pipeline that ingests raw CRM data, applies a feature engineering '
                    'layer (normalisation, ordinal encoding, interaction terms), trains an XGBoost classifier, '
                    'and pushes churn probability scores to a PostgreSQL dashboard consumed by the CRM team. '
                    'Great Expectations validates data quality at each stage; Prefect orchestrates the schedule; '
                    'MLflow tracks every experiment with full model registry support.\n\n'
                    'The standout feature is drift detection: Kolmogorov–Smirnov tests run nightly on each feature. '
                    'When any feature drifts beyond a configurable threshold, Prefect automatically triggers a '
                    'retraining job with fresh data. In production, the model stayed accurate 3 months beyond '
                    'the initial training cutoff thanks to this feedback loop — a critical win for a SaaS client '
                    'with 50K active users.'
                ),
                'subtitle': 'Self-retraining MLOps pipeline with drift detection that keeps churn predictions fresh automatically.',
                'year': '2025',
                'role': 'ML Engineer / MLOps',
                'duration': '4 Months',
                'team_size': 'Solo Project',
                'tags': 'XGBoost, MLflow, Prefect, PostgreSQL, Grafana, Great Expectations',
                'category': 'data',
                'image_url': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&auto=format&fit=crop',
                'show_on_index': True,
                'order': 3,
                'highlights': [
                    {'icon': 'chart', 'value': '91.5%', 'label': 'Churn Recall'},
                    {'icon': 'users', 'value': '50K+', 'label': 'Users Monitored'},
                    {'icon': 'clock', 'value': 'Nightly', 'label': 'Drift Checks'},
                    {'icon': 'star', 'value': '4.9★', 'label': 'Client Rating'},
                ],
                'detail_images': [
                    {
                        'url': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1200&auto=format&fit=crop',
                        'alt': 'Grafana Monitoring Dashboard',
                        'caption': 'Grafana Churn Monitoring Dashboard',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop',
                        'alt': 'MLflow Experiment Tracker',
                        'caption': 'MLflow Experiment Tracking UI',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800&auto=format&fit=crop',
                        'alt': 'Prefect Pipeline DAG',
                        'caption': 'Prefect Orchestration Pipeline DAG',
                    },
                ],
                'diagrams': [
                    {
                        'url': 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop',
                        'label': 'Architecture',
                        'title': 'MLOps Pipeline Architecture',
                        'desc': 'CRM data → Great Expectations → Prefect DAG → XGBoost training → MLflow registry → PostgreSQL → Grafana.',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1607705703571-c5a8695f18f6?w=800&auto=format&fit=crop',
                        'label': 'Drift Detection',
                        'title': 'Automated Retraining Trigger Flow',
                        'desc': 'Nightly KS-test on feature distributions — if drift > threshold, Prefect fires a full retraining and model registry update.',
                    },
                ],
                'timeline_phases': [
                    {
                        'phase': 'Phase 01', 'date': 'Jul 2025',
                        'title': 'Data Audit & Feature Engineering',
                        'desc': 'Audited 18 months of CRM data, handled 12% missing values, and engineered 35 features including RFM scores and tenure-based interaction terms.',
                    },
                    {
                        'phase': 'Phase 02', 'date': 'Aug 2025',
                        'title': 'Model Training & MLflow Tracking',
                        'desc': 'Trained XGBoost with Optuna hyperparameter search over 100 trials, tracked every run in MLflow, and registered the best model with full artifact logging.',
                    },
                    {
                        'phase': 'Phase 03', 'date': 'Sep 2025',
                        'title': 'Orchestration & Data Validation',
                        'desc': 'Built Prefect DAG for nightly runs, integrated Great Expectations data quality checks, and set up KS-test drift detection with configurable thresholds.',
                    },
                    {
                        'phase': 'Phase 04', 'date': 'Oct 2025',
                        'title': 'Dashboard & Production Rollout',
                        'desc': 'Pushed churn scores to PostgreSQL, built Grafana monitoring boards, and rolled out to production serving 50K users with zero downtime.',
                    },
                ],
                'github_url': 'https://github.com/ProjectsHub/customer-churn-pipeline',
                'project_url': '',
                'price': 4999,
                'price_label': '₹4,999',
                'price_features': [
                    'Full pipeline source code (Prefect DAGs + training scripts)',
                    'Pre-trained XGBoost model + MLflow experiment logs',
                    'Docker Compose stack (Prefect, MLflow, Grafana, PostgreSQL)',
                    'Great Expectations data suite configuration',
                    '75-minute video walkthrough',
                    '45-day email support',
                ],
            },
            {
                'title': 'RAG Document Q&A',
                'description': 'Retrieval-Augmented Generation system for private document Q&A using LangChain, FAISS vector search, and GPT-4 — supporting conversational follow-up questions.',
                'detailed_description': (
                    'Upload any set of PDFs or text documents and ask questions in plain English. '
                    'The system chunks documents using a recursive character splitter, embeds each chunk with '
                    'OpenAI text-embedding-3-small, and stores vectors in a FAISS index on disk. At query time, '
                    'a custom LangChain RetrievalQA chain performs MMR (Maximum Marginal Relevance) retrieval '
                    'followed by a cross-encoder re-ranking step to surface the most relevant context before '
                    'passing it to GPT-4. A conversation buffer memory window enables multi-turn follow-up '
                    'questions that reference prior answers.\n\n'
                    'Key innovations: a hybrid sparse-dense retrieval step (BM25 + FAISS) that outperforms '
                    'pure dense retrieval by 9% on domain-specific corpora, and a citation overlay that '
                    'highlights the exact document passage used to generate each answer — critical for '
                    'legal and compliance use cases where auditability matters.'
                ),
                'subtitle': 'Private document Q&A with hybrid retrieval, citation overlay, and multi-turn conversation.',
                'year': '2025',
                'role': 'AI Engineer',
                'duration': '6 Weeks',
                'team_size': 'Solo Project',
                'tags': 'LangChain, FAISS, GPT-4, FastAPI, Streamlit, BM25',
                'category': 'ml',
                'image_url': 'https://images.unsplash.com/photo-1607705703571-c5a8695f18f6?w=900&auto=format&fit=crop',
                'show_on_index': False,
                'order': 4,
                'highlights': [
                    {'icon': 'chart', 'value': '9%', 'label': 'Retrieval Gain'},
                    {'icon': 'clock', 'value': '<2s', 'label': 'Answer Latency'},
                    {'icon': 'users', 'value': '500+', 'label': 'Docs Supported'},
                    {'icon': 'star', 'value': '4.9★', 'label': 'User Rating'},
                ],
                'detail_images': [
                    {
                        'url': 'https://images.unsplash.com/photo-1607705703571-c5a8695f18f6?w=1200&auto=format&fit=crop',
                        'alt': 'RAG Chat Interface',
                        'caption': 'Streamlit Document Q&A Chat Interface',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1456324463128-7ff6903988d8?w=800&auto=format&fit=crop',
                        'alt': 'Document Upload Flow',
                        'caption': 'PDF Upload & Chunking Interface',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop',
                        'alt': 'Citation Highlight Panel',
                        'caption': 'Source Citation Highlight Overlay',
                    },
                ],
                'diagrams': [
                    {
                        'url': 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop',
                        'label': 'Architecture',
                        'title': 'RAG System Architecture',
                        'desc': 'PDF → chunker → embedder → FAISS index → hybrid BM25+dense retrieval → re-ranker → GPT-4 → answer + citations.',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800&auto=format&fit=crop',
                        'label': 'Retrieval Flow',
                        'title': 'Hybrid Retrieval & Re-ranking Pipeline',
                        'desc': 'How BM25 sparse candidates and FAISS dense candidates are merged, de-duplicated, and re-ranked by a cross-encoder before being passed to GPT-4.',
                    },
                ],
                'timeline_phases': [
                    {
                        'phase': 'Phase 01', 'date': 'Oct 2025',
                        'title': 'Ingestion & Embedding Pipeline',
                        'desc': 'Built PDF loader, recursive character chunker, and OpenAI embedding pipeline. Benchmarked chunk sizes from 256 to 1024 tokens on retrieval quality.',
                    },
                    {
                        'phase': 'Phase 02', 'date': 'Oct 2025',
                        'title': 'Hybrid Retrieval & Re-ranking',
                        'desc': 'Implemented BM25 sparse retrieval, merged with FAISS dense results, and added cross-encoder re-ranking step — lifting retrieval precision by 9%.',
                    },
                    {
                        'phase': 'Phase 03', 'date': 'Nov 2025',
                        'title': 'LangChain Chain & Conversation Memory',
                        'desc': 'Wired custom RetrievalQA chain with conversation buffer window memory for multi-turn Q&A and built citation passage highlighting logic.',
                    },
                    {
                        'phase': 'Phase 04', 'date': 'Nov 2025',
                        'title': 'Streamlit UI & FastAPI Deployment',
                        'desc': 'Built Streamlit frontend with chat UI, deployed FastAPI backend on Railway, and added role-based document access control.',
                    },
                ],
                'github_url': 'https://github.com/ProjectsHub/rag-document-qa',
                'project_url': '',
                'price': 5999,
                'price_label': '₹5,999',
                'price_features': [
                    'Full source code (FastAPI backend + Streamlit UI)',
                    'Pre-built FAISS index on a sample legal corpus',
                    'Docker Compose deployment setup',
                    'LangChain custom chain explanation notebook',
                    '90-minute video walkthrough',
                    '60-day email support',
                ],
            },
            {
                'title': 'Real-time Data Dashboard',
                'description': 'Scalable Kafka → Spark Streaming → ClickHouse pipeline ingesting 100K+ events/second, visualised in a self-service Apache Superset dashboard on Kubernetes.',
                'detailed_description': (
                    'A fully cloud-native streaming analytics stack built for a FinTech client needing sub-second '
                    'visibility into transaction events. Apache Kafka ingests 100K+ events per second across '
                    '12 topics. Spark Structured Streaming consumers apply windowed aggregations (1-min, 5-min, '
                    '1-hour), detect anomalies using a streaming z-score algorithm, and land results into '
                    'ClickHouse. ClickHouse materialized views serve the Superset dashboards with query response '
                    'times under 300ms even at 100M+ row tables.\n\n'
                    'The entire stack runs on Kubernetes with Helm charts. Kafka and ClickHouse are horizontally '
                    'scaled via custom HPA policies triggered by consumer lag and query throughput respectively. '
                    'A GitOps workflow (ArgoCD) handles deployments, making environment promotion from staging '
                    'to production a one-click operation.'
                ),
                'subtitle': 'Kafka-to-ClickHouse streaming analytics handling 100K events/second with sub-300ms query response.',
                'year': '2024',
                'role': 'Data Engineer',
                'duration': '5 Months',
                'team_size': '2-person team',
                'tags': 'Kafka, Spark, ClickHouse, Superset, Kubernetes, Helm, ArgoCD',
                'category': 'data',
                'image_url': 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&auto=format&fit=crop',
                'show_on_index': False,
                'order': 5,
                'highlights': [
                    {'icon': 'users', 'value': '100K+', 'label': 'Events/Second'},
                    {'icon': 'clock', 'value': '<300ms', 'label': 'Query Latency'},
                    {'icon': 'chart', 'value': '100M+', 'label': 'Rows in ClickHouse'},
                    {'icon': 'star', 'value': '4.8★', 'label': 'Client Rating'},
                ],
                'detail_images': [
                    {
                        'url': 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=1200&auto=format&fit=crop',
                        'alt': 'Superset Dashboard',
                        'caption': 'Apache Superset Real-time Dashboard',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800&auto=format&fit=crop',
                        'alt': 'Kafka Consumer Lag Monitor',
                        'caption': 'Kafka Consumer Lag Monitoring',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop',
                        'alt': 'ClickHouse Query Performance',
                        'caption': 'ClickHouse Query Performance Panel',
                    },
                ],
                'diagrams': [
                    {
                        'url': 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop',
                        'label': 'Architecture',
                        'title': 'Streaming Pipeline Architecture',
                        'desc': 'Producers → Kafka → Spark Structured Streaming → ClickHouse materialized views → Superset dashboards.',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1607705703571-c5a8695f18f6?w=800&auto=format&fit=crop',
                        'label': 'K8s Infra',
                        'title': 'Kubernetes & GitOps Deployment',
                        'desc': 'Helm chart structure, HPA scaling policies for Kafka and ClickHouse, and ArgoCD GitOps promotion pipeline.',
                    },
                ],
                'timeline_phases': [
                    {
                        'phase': 'Phase 01', 'date': 'Jun 2024',
                        'title': 'Infrastructure & Kafka Setup',
                        'desc': 'Provisioned Kubernetes cluster on GKE, deployed Kafka via Helm with 12-topic configuration, and load-tested to 150K events/second.',
                    },
                    {
                        'phase': 'Phase 02', 'date': 'Aug 2024',
                        'title': 'Spark Streaming Consumers',
                        'desc': 'Built Spark Structured Streaming jobs for 1-min, 5-min, and 1-hour windowed aggregations with exactly-once semantics and a streaming anomaly detector.',
                    },
                    {
                        'phase': 'Phase 03', 'date': 'Sep 2024',
                        'title': 'ClickHouse & Superset',
                        'desc': 'Designed ClickHouse schema with materialized views for common aggregation patterns. Built 8 Superset dashboards with drilldown filters for the client BI team.',
                    },
                    {
                        'phase': 'Phase 04', 'date': 'Oct 2024',
                        'title': 'GitOps & Autoscaling',
                        'desc': 'Set up ArgoCD for GitOps deployments, configured HPA policies, and handed over runbooks for on-call operations to the client team.',
                    },
                ],
                'github_url': 'https://github.com/ProjectsHub/realtime-data-dashboard',
                'project_url': '',
                'price': 6999,
                'price_label': '₹6,999',
                'price_features': [
                    'Full source code (Kafka producers, Spark jobs, Helm charts)',
                    'ClickHouse schema + materialized view definitions',
                    'ArgoCD GitOps pipeline configuration',
                    'Superset dashboard JSON exports',
                    '90-minute video walkthrough',
                    '60-day email support',
                ],
            },
            {
                'title': 'Multi-Cloud Cost Optimiser',
                'description': 'Python automation tool that analyses AWS and GCP billing APIs, identifies waste (idle instances, unused EBS, orphaned snapshots), and auto-generates Terraform remediation scripts.',
                'detailed_description': (
                    'A CLI and scheduled-job tool that pulls granular billing data from AWS Cost Explorer and '
                    'the GCP Billing API, normalises it into a unified cost model, and runs a rule engine '
                    'against it. Rules catch common waste patterns: instances idle >80% over 7 days, '
                    'unattached EBS volumes older than 30 days, orphaned snapshots, reserved instance '
                    'coverage gaps, and data transfer anomalies. Each finding is ranked by monthly savings '
                    'potential and exported to a pandas-powered HTML report.\n\n'
                    'For findings that can be safely automated, the tool generates ready-to-apply Terraform '
                    'snippets (right-sizing, snapshot cleanup, RI purchase recommendations). In production '
                    'for a Series-B SaaS startup, the first run identified $3,400/month in savings; after '
                    'applying the generated scripts, the client achieved a 37% infrastructure cost reduction '
                    'within one billing cycle — with zero disruption to running workloads.'
                ),
                'subtitle': 'Automated cloud waste detection that cut infrastructure spend by 37% for a SaaS startup.',
                'year': '2024',
                'role': 'Cloud Engineer',
                'duration': '6 Weeks',
                'team_size': 'Solo Project',
                'tags': 'Python, AWS, GCP, Terraform, pandas, boto3, Click',
                'category': 'cloud',
                'image_url': 'https://images.unsplash.com/photo-1607705703571-c5a8695f18f6?w=800&auto=format&fit=crop',
                'show_on_index': False,
                'order': 6,
                'highlights': [
                    {'icon': 'chart', 'value': '37%', 'label': 'Cost Reduction'},
                    {'icon': 'users', 'value': '$3.4K', 'label': 'Monthly Savings Found'},
                    {'icon': 'clock', 'value': '2 clouds', 'label': 'AWS + GCP'},
                    {'icon': 'star', 'value': '4.9★', 'label': 'Client Rating'},
                ],
                'detail_images': [
                    {
                        'url': 'https://images.unsplash.com/photo-1607705703571-c5a8695f18f6?w=1200&auto=format&fit=crop',
                        'alt': 'Cost Report HTML Output',
                        'caption': 'Automated HTML Cost Savings Report',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&auto=format&fit=crop',
                        'alt': 'CLI Tool Interface',
                        'caption': 'Click CLI Interface & Rule Engine Output',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop',
                        'alt': 'Terraform Snippet Output',
                        'caption': 'Auto-generated Terraform Remediation Snippets',
                    },
                ],
                'diagrams': [
                    {
                        'url': 'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=800&auto=format&fit=crop',
                        'label': 'Architecture',
                        'title': 'Tool Architecture & Data Flow',
                        'desc': 'AWS Cost Explorer + GCP Billing API → normaliser → rule engine → findings ranker → HTML report + Terraform snippets.',
                    },
                    {
                        'url': 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&auto=format&fit=crop',
                        'label': 'Rule Engine',
                        'title': 'Waste Detection Rule Categories',
                        'desc': 'Overview of all 14 waste-detection rules across compute, storage, network, and reservation coverage categories.',
                    },
                ],
                'timeline_phases': [
                    {
                        'phase': 'Phase 01', 'date': 'Aug 2024',
                        'title': 'Billing API Integration',
                        'desc': 'Integrated AWS Cost Explorer and GCP Billing API via boto3 and google-cloud-billing. Built unified cost model to normalise spend data across clouds.',
                    },
                    {
                        'phase': 'Phase 02', 'date': 'Aug 2024',
                        'title': 'Rule Engine Development',
                        'desc': 'Designed 14 waste-detection rules covering idle EC2/GCE instances, unattached volumes, orphaned snapshots, and RI coverage gaps. Each rule outputs a monthly savings estimate.',
                    },
                    {
                        'phase': 'Phase 03', 'date': 'Sep 2024',
                        'title': 'Terraform Generation & Reports',
                        'desc': 'Built Terraform snippet generator for safe remediations and a pandas-powered HTML report ranked by savings potential. CLI packaged with Click and distributed via PyPI.',
                    },
                    {
                        'phase': 'Phase 04', 'date': 'Sep 2024',
                        'title': 'Production Deployment & Results',
                        'desc': 'Deployed as a weekly Lambda scheduled job for the client. First run identified $3,400/month savings; scripts applied with zero disruption achieved 37% cost reduction.',
                    },
                ],
                'github_url': 'https://github.com/ProjectsHub/multi-cloud-cost-optimiser',
                'project_url': '',
                'price': 3499,
                'price_label': '₹3,499',
                'price_features': [
                    'Full Python source code (CLI + Lambda scheduler)',
                    'All 14 waste-detection rules with documentation',
                    'Terraform snippet generator templates',
                    'AWS + GCP IAM permission setup guide',
                    '60-minute video walkthrough',
                    '30-day email support',
                ],
            },
        ]

        updated = 0
        created = 0
        for data in projects:
            data = dict(data)

            # These are related rows, not Project columns — pull them out
            # before update_or_create, which would otherwise try to assign
            # to the reverse side of the relation and raise TypeError.
            highlights = data.pop('highlights', [])
            timeline_phases = data.pop('timeline_phases', [])
            price_features = data.pop('price_features', [])
            # detail_images / diagrams are ImageFields backed by real uploaded
            # files, so the sample external URLs here cannot be seeded. Add
            # them from the admin instead.
            data.pop('detail_images', None)
            data.pop('diagrams', None)

            project, is_new = Project.objects.update_or_create(
                title=data['title'], defaults=data
            )

            # Re-seed children so repeated runs stay idempotent
            project.highlights.all().delete()
            ProjectHighlight.objects.bulk_create([
                ProjectHighlight(project=project, order=i, **h)
                for i, h in enumerate(highlights)
            ])

            project.timeline_phases.all().delete()
            ProjectTimelinePhase.objects.bulk_create([
                ProjectTimelinePhase(project=project, order=i, **t)
                for i, t in enumerate(timeline_phases)
            ])

            project.price_features.all().delete()
            ProjectFeature.objects.bulk_create([
                ProjectFeature(project=project, text=text, order=i)
                for i, text in enumerate(price_features)
            ])

            if is_new:
                created += 1
            else:
                updated += 1
        self.stdout.write(f'  Projects: {created} created, {updated} updated')

    # ── Workshops ─────────────────────────────────────────────────────────────

    def _seed_workshops(self):
        ws_data = {
            'title': 'End-to-End ML Engineering Bootcamp',
            'subtitle': 'From data to deployment in 4 intensive days',
            'description': (
                'Master the full machine-learning lifecycle — from EDA and feature engineering '
                'to model training, evaluation, and production deployment. '
                'You will leave with three portfolio-ready projects and hands-on MLOps experience.'
            ),
            'date': 'Jun 7 – 10, 2026',
            'time': '10 AM – 5 PM IST',
            'seats': 25,
            'mode': 'Online (Live)',
            'price': 999,
            'price_label': '₹999',
            'is_featured': True,
            'order': 1,
        }
        ws, is_new = WorkshopCard.objects.update_or_create(
            title=ws_data['title'], defaults=ws_data
        )
        days = [
            (1, 'Data & EDA', 'Saturday, Jun 7',
             'Deep dive into real-world datasets. Pandas, Matplotlib, Seaborn, missing-value strategies, and correlation analysis.',
             'A polished EDA notebook you can include in your portfolio'),
            (2, 'Feature Engineering & Modelling', 'Sunday, Jun 8',
             'Build feature pipelines with sklearn. Train and compare multiple algorithms, tune hyperparameters, and interpret results.',
             'Trained, tuned, and documented ML model'),
            (3, 'Deep Learning & Computer Vision', 'Saturday, Jun 9',
             'PyTorch fundamentals, CNN architectures, transfer learning with ResNet, and real-time inference.',
             'Working image classifier with >90% accuracy'),
            (4, 'MLOps & Deployment', 'Sunday, Jun 10',
             'Package models with FastAPI, containerise with Docker, run CI/CD with GitHub Actions, and deploy to the cloud.',
             'Deployed API endpoint accessible from anywhere'),
        ]
        days_created = 0
        for num, title, date_label, desc, outcome in days:
            _, created = WorkshopDay.objects.update_or_create(
                workshop=ws, day_number=num,
                defaults={'title': title, 'date_label': date_label,
                          'description': desc, 'outcome': outcome}
            )
            if created:
                days_created += 1
        self.stdout.write(f'  Workshops: {"1 created" if is_new else "1 updated"}, {days_created} days created')

    # ── Pricing ───────────────────────────────────────────────────────────────

    def _seed_pricing(self):
        plans = [
            {
                'meta': {
                    'name': 'Starter', 'icon_type': 'basic',
                    'description': 'Perfect for students and solo learners',
                    'monthly_price': 0, 'yearly_price': 0,
                    'is_free': True, 'order': 1, 'cta_label': 'Get Started Free',
                },
                'features': [
                    'Access to 3 free projects',
                    'Community Discord access',
                    'Monthly newsletter',
                    'Basic tutorials',
                ],
            },
            {
                'meta': {
                    'name': 'Pro', 'icon_type': 'pro',
                    'description': 'For serious ML practitioners',
                    'monthly_price': 999, 'yearly_price': 799,
                    'monthly_original': 1499, 'yearly_original': 1199,
                    'is_featured': True, 'order': 2, 'cta_label': 'Start Pro',
                },
                'features': [
                    'All projects with source code',
                    'Priority Discord support',
                    'Monthly live Q&A sessions',
                    'Workshop discounts (20%)',
                    'Certificate of completion',
                    'Private project reviews',
                ],
            },
            {
                'meta': {
                    'name': 'Enterprise', 'icon_type': 'enterprise',
                    'description': 'For teams and organisations',
                    'monthly_price': 4999, 'yearly_price': 3999,
                    'order': 3, 'cta_label': 'Contact Us',
                },
                'features': [
                    'Everything in Pro',
                    'Custom project builds',
                    'Dedicated mentor sessions',
                    'Team seat management',
                    'Invoicing & GST receipts',
                    'SLA support',
                ],
            },
        ]
        created_plans = 0
        for plan_data in plans:
            plan, is_new = PricingPlan.objects.update_or_create(
                name=plan_data['meta']['name'],
                defaults=plan_data['meta']
            )
            if is_new:
                created_plans += 1
                for i, feature_text in enumerate(plan_data['features']):
                    PricingFeature.objects.create(plan=plan, feature=feature_text, order=i)
        self.stdout.write(f'  Pricing plans: {created_plans} created')
