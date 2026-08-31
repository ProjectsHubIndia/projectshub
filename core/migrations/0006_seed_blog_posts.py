"""Carry the three hardcoded blog posts into the new BlogPost tables.

blog.html / blog_detail.html previously held this content inline behind
`{% if blog_id == N %}` branches. Seeding it here means the blog page is not
empty the moment the dynamic templates go live.
"""
from datetime import date
from django.db import migrations


POSTS = [
    {
        'slug': 'building-your-first-llm-app-with-python',
        'title': 'Building Your First LLM App with Python',
        'category': 'ai-tutorials',
        'excerpt': (
            'Learn step-by-step how to integrate the OpenAI API into a Django '
            'web application and create a smart chatbot.'
        ),
        'lead': (
            'Large Language Models (LLMs) have revolutionized the way we build '
            'software. In this tutorial, we will explore how to set up your '
            'environment, connect to the OpenAI API, and build your very first '
            'AI-powered application using Django.'
        ),
        'emoji': '🤖',
        'gradient_from': '#2563eb', 'gradient_to': '#3b82f6', 'accent': '#3b82f6',
        'read_time': '5 min read',
        'published_at': date(2026, 7, 13),
        'order': 1,
        'sections': [
            {
                'heading': '1. Setting up the Environment',
                'body': (
                    'Before we start writing code, we need to ensure our Python '
                    'environment is ready. It is highly recommended to use a '
                    'virtual environment to manage dependencies.'
                ),
                'code': 'python -m venv venv\nsource venv/bin/activate\npip install django openai',
            },
            {
                'heading': '2. Writing the Integration Code',
                'body': (
                    'Once the dependencies are installed, you can create a simple '
                    'utility function that interacts with the OpenAI ChatCompletion '
                    'endpoint. Keep your API keys secure!'
                ),
                'code': (
                    'import openai\n\n'
                    'def get_ai_response(prompt):\n'
                    '    response = openai.ChatCompletion.create(\n'
                    '        model="gpt-4",\n'
                    '        messages=[{"role": "user", "content": prompt}]\n'
                    '    )\n'
                    '    return response.choices[0].message.content'
                ),
            },
            {
                'heading': 'Conclusion',
                'body': (
                    'Building AI applications is easier than ever. With just a few '
                    'lines of code, you can unlock incredible capabilities. Stay '
                    "tuned for our next post where we'll discuss deploying your "
                    'Django app to production!'
                ),
                'code': '',
            },
        ],
    },
    {
        'slug': 'how-to-stand-out-in-tech-interviews',
        'title': 'How to Stand Out in Tech Interviews',
        'category': 'career',
        'excerpt': (
            'Stop grinding LeetCode all day. Here is what engineering managers '
            'are actually looking for when hiring new developers.'
        ),
        'lead': (
            'Stop grinding LeetCode all day. Here is what engineering managers '
            'are actually looking for when hiring new developers — and how you '
            'can stand out in every round.'
        ),
        'emoji': '💼',
        'gradient_from': '#10b981', 'gradient_to': '#34d399', 'accent': '#10b981',
        'read_time': '7 min read',
        'published_at': date(2026, 7, 10),
        'order': 2,
        'sections': [
            {
                'heading': '1. Show Your Thinking, Not Just Your Answer',
                'body': (
                    'Interviewers care far more about how you approach a problem '
                    'than whether you get the perfect solution. Talk through your '
                    'thought process out loud. Ask clarifying questions before '
                    'jumping to code.'
                ),
                'code': '',
            },
            {
                'heading': '2. Build Real Projects',
                'body': (
                    'A GitHub with 3 strong, complete projects beats 100 '
                    'half-finished repos. Pick projects that solve a real problem '
                    'and explain the business impact in your README and resume. '
                    'Recruiters notice.'
                ),
                'code': (
                    '# Good README structure\n'
                    '## Problem Statement\n'
                    '## Solution & Architecture\n'
                    '## Demo / Screenshots\n'
                    '## How to Run'
                ),
            },
            {
                'heading': '3. Prepare Behavioral Questions',
                'body': (
                    'Most interviews fail not on the technical side but on soft '
                    'skills. Prepare 5–7 strong STAR (Situation, Task, Action, '
                    'Result) stories that you can adapt to different questions '
                    'about teamwork, failure, and leadership.'
                ),
                'code': '',
            },
            {
                'heading': 'Conclusion',
                'body': (
                    'Tech interviews are a skill you can learn. Focus on '
                    'communication, real projects, and consistent practice — and '
                    'you will land the offer.'
                ),
                'code': '',
            },
        ],
    },
    {
        'slug': 'from-zero-to-mvp-in-3-weeks',
        'title': 'From Zero to MVP in 3 Weeks',
        'category': 'case-study',
        'excerpt': (
            'A deep dive into how we helped a startup launch their AI-powered '
            'SaaS product and acquire their first 100 users.'
        ),
        'lead': (
            'A deep dive into how we helped a startup launch their AI-powered '
            'SaaS product and acquire their first 100 users — all within 3 weeks '
            'of kickoff.'
        ),
        'emoji': '🚀',
        'gradient_from': '#f59e0b', 'gradient_to': '#fbbf24', 'accent': '#f59e0b',
        'read_time': '4 min read',
        'published_at': date(2026, 7, 5),
        'order': 3,
        'sections': [
            {
                'heading': 'The Challenge',
                'body': (
                    'Our client had a great idea for an AI document summarizer for '
                    'law firms. They had no technical team, a tight budget, and a '
                    'demo deadline set by a potential investor in 3 weeks.'
                ),
                'code': '',
            },
            {
                'heading': 'Week 1 — Design & Architecture',
                'body': (
                    'We spent the first week defining the core feature set, '
                    'designing the UI in Figma, and setting up the Django + OpenAI '
                    'backend. Scope discipline was critical — we said no to 80% of '
                    'the initial feature wishlist.'
                ),
                'code': '',
            },
            {
                'heading': 'Week 2 — Build & Integrate',
                'body': (
                    'Core development: PDF upload, OpenAI GPT-4 integration for '
                    'summarization, user authentication, and a clean results '
                    'dashboard. We shipped to a staging URL at the end of Day 12.'
                ),
                'code': '',
            },
            {
                'heading': 'Week 3 — Launch & First Users',
                'body': (
                    'We deployed to production, ran a soft launch on LinkedIn, and '
                    'helped the client acquire their first 100 beta users. The '
                    'investor demo went ahead — and they closed a seed round the '
                    'following month.'
                ),
                'code': '',
            },
            {
                'heading': 'Key Takeaway',
                'body': (
                    'Speed wins when you have discipline. A focused MVP with one '
                    'killer feature beats a bloated product every time. If you have '
                    'an idea, start small and ship fast.'
                ),
                'code': '',
            },
        ],
    },
]


def seed(apps, schema_editor):
    BlogPost = apps.get_model('core', 'BlogPost')
    BlogSection = apps.get_model('core', 'BlogSection')
    for data in POSTS:
        sections = data.pop('sections')
        post, created = BlogPost.objects.get_or_create(
            slug=data['slug'], defaults=data
        )
        if not created:
            continue
        for i, s in enumerate(sections):
            BlogSection.objects.create(post=post, order=i, **s)


def unseed(apps, schema_editor):
    BlogPost = apps.get_model('core', 'BlogPost')
    BlogPost.objects.filter(slug__in=[p['slug'] for p in POSTS]).delete()


class Migration(migrations.Migration):
    dependencies = [('core', '0005_blogpost_blogsection')]
    operations = [migrations.RunPython(seed, unseed)]
