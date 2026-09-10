"""Create the six AI tool projects from the ProjectsHub screenshots.

Idempotent: matches on title, so re-running updates nothing that already
exists. Pass --replace to wipe and rebuild just these six.

Every detail here is taken from the app screenshots. Fields that depend on
business decisions or external links (price, project_url, github_url,
case_study_url, youtube_url, role, duration, team_size) are deliberately left
blank for you to fill in from the admin.
"""
from django.core.management.base import BaseCommand
from core.models import (
    Project, ProjectImage, ProjectHighlight,
    ProjectDiagram, ProjectTimelinePhase, ProjectFeature,
)

PROJECTS = [
    {
        'title': 'Aria — Multi-Persona AI Assistant',
        'subtitle': 'A production chat assistant that changes its voice to match the job',
        'category': 'ml',
        'tags': 'Django, LLM, Chat UI, REST API, Personas',
        'image': 'projects/aria-chatbot.jpeg',
        'year': '2026',
        'description': (
            'A full-featured AI chat assistant with switchable personas, a curated '
            'prompt-starter library and one-tap quick actions — so users get a useful '
            'answer without knowing how to write a prompt.'
        ),
        'detailed_description': (
            'Aria is a chat assistant built around a simple observation: most people '
            'do not know what to type into a blank chat box. Instead of one generic '
            'bot, Aria ships four tuned personas — Helpful Assistant for clear, '
            'balanced answers, Creative Writer for stories and bold ideas, Code Expert '
            'for debugging and reviews, and Brainstorm Buddy for rapid, no-judgment '
            'ideation — and users can define their own on top of those.\n\n'
            'The left rail carries a prompt-starter library grouped by intent '
            '(Writing, Ideas, Learn) plus a "Surprise me" generator, so the first '
            'message is always one click away. The right rail turns the most common '
            'requests into Quick Actions — Summarize Text, Generate Ideas, Improve '
            'Writing and Code Assistant — and lets users pin any answer worth keeping '
            'back to the session.\n\n'
            'The result is a chat product that stays useful for a first-time user and '
            'a power user at the same time, without either one hitting an empty screen.'
        ),
        'highlights': [
            ('users', '4+', 'Tuned Personas'),
            ('bolt', '4', 'One-Tap Quick Actions'),
            ('star', '6', 'Prompt Starters'),
            ('clock', 'Live', 'Session History'),
        ],
        'features': [
            'Four tuned personas — Helpful Assistant, Creative Writer, Code Expert, Brainstorm Buddy',
            'Custom persona builder for defining your own assistant',
            'Prompt-starter library grouped by Writing, Ideas and Learn',
            '"Surprise me with a prompt" generator for cold starts',
            'Quick Actions: Summarize Text, Generate Ideas, Improve Writing, Code Assistant',
            'Pin any reply to keep it in the session',
            'Per-session chat history with message counter',
            'Dark, focused chat interface',
        ],
        'timeline': [
            ('Phase 01', 'Discovery', 'Persona & Prompt Research',
             'Mapped the four jobs users actually bring to a chatbot and wrote a tuned '
             'system prompt for each one.'),
            ('Phase 02', 'Build', 'Chat Engine & API',
             'Built the Django chat backend, streaming responses, session handling and '
             'the persona-switching layer.'),
            ('Phase 03', 'Build', 'Guided Entry Points',
             'Added the prompt-starter library, Quick Actions and pinned replies to '
             'remove the blank-page problem.'),
            ('Phase 04', 'Launch', 'Polish & Ship',
             'Dark UI pass, empty states, tips and the upgrade path.'),
        ],
    },
    {
        'title': 'CodeLens — AI Code Reviewer & Explainer',
        'subtitle': 'Paste code, get a line-by-line explanation a junior can follow',
        'category': 'ml',
        'tags': 'Django, LLM, Code Analysis, Python, JavaScript',
        'image': 'projects/codelens.jpeg',
        'year': '2026',
        'description': (
            'A code comprehension tool that turns any snippet into a structured '
            'breakdown — plain-English summary, numbered walkthrough and the key '
            'concepts behind it — then answers follow-up questions about it.'
        ),
        'detailed_description': (
            'CodeLens exists for the moment you inherit code you did not write. Paste '
            'or upload a snippet, pick the language, and it returns a Code Breakdown '
            'in three layers: a high-level Summary for orientation, a numbered '
            'Step-by-step Explanation that walks each construct in order, and a Key '
            'Concepts strip that names the techniques in play — for loops, range(), '
            'variables — so the reader learns the pattern, not just this file.\n\n'
            'The explanation panel is conversational. Once analysis completes, users '
            'can ask follow-up questions inline, or jump straight to one of three '
            'framed asks: Optimization, Bug Fixing, or Test Cases. A live status bar '
            'tracks line count and detected issues, and any breakdown can be exported.\n\n'
            'The interface is deliberately split — source on the left, explanation on '
            'the right — so the reader never loses their place in the code while '
            'reading about it.'
        ),
        'highlights': [
            ('chart', '3-Layer', 'Code Breakdown'),
            ('bolt', '2', 'Languages Supported'),
            ('star', '3', 'Framed Follow-Ups'),
            ('clock', 'Live', 'Issue Detection'),
        ],
        'features': [
            'Plain-English summary, step-by-step walkthrough and key-concept tagging',
            'Python and JavaScript analysis modes',
            'Paste, upload or clear source directly in the editor pane',
            'Inline follow-up questions on any completed analysis',
            'One-tap Optimization, Bug Fixing and Test Cases prompts',
            'Live line count and issue counter',
            'Export the generated breakdown',
            'Split source / explanation layout with light and dark themes',
        ],
        'timeline': [
            ('Phase 01', 'Discovery', 'Explanation Format',
             'Tested breakdown formats with real developers and settled on the '
             'summary / walkthrough / concepts structure.'),
            ('Phase 02', 'Build', 'Analysis Pipeline',
             'Built language detection, the prompt chain behind each layer and the '
             'streaming explanation renderer.'),
            ('Phase 03', 'Build', 'Conversational Layer',
             'Added follow-up Q&A over the analysed snippet plus the framed '
             'Optimization, Bug Fixing and Test Case actions.'),
            ('Phase 04', 'Launch', 'Editor Experience',
             'Split-pane layout, upload and export, issue counter and theme support.'),
        ],
    },
    {
        'title': 'GrammarLens — AI Grammar Checker',
        'subtitle': 'Every correction comes with the reason behind it',
        'category': 'ml',
        'tags': 'Django, NLP, LLM, Writing Tools',
        'image': 'projects/grammarlens.jpeg',
        'year': '2026',
        'description': (
            'A writing assistant that scores your text, flags each issue inline, and '
            'explains the grammar rule behind every suggestion instead of silently '
            'rewriting you.'
        ),
        'detailed_description': (
            'Most grammar tools fix your sentence and move on. GrammarLens teaches '
            'while it corrects. Text is scored out of 100 with a plain-language verdict '
            '("Looking good — 3 issues to review"), and every problem is underlined in '
            'place so the writer sees it in context.\n\n'
            'Each suggestion is a before → after pair with a written explanation of the '
            'rule: why "gone" should be "has gone" (present perfect after "she" for a '
            'recently completed action), why "dont" should be "doesn\'t" (correct form '
            'to use with "he"), why "nothing" should be "anything". Fixes can be '
            'applied one at a time or all at once, and the corrected text copies to '
            'the clipboard in a single click.\n\n'
            'The editor keeps a live character count and a clean toggle between '
            'reviewing and editing, so the writer stays in flow.'
        ),
        'highlights': [
            ('chart', '/100', 'Writing Score'),
            ('star', 'Every', 'Fix Explained'),
            ('bolt', '1-Tap', 'Apply All Fixes'),
            ('clock', 'Live', 'Inline Highlighting'),
        ],
        'features': [
            'Writing score out of 100 with a plain-language verdict',
            'Inline underlining of every issue in the original text',
            'Before → after suggestion cards with the grammar rule explained',
            'Apply a single fix or all fixes at once',
            'Copy the corrected text in one click',
            'Toggle between review and edit modes',
            'Live character count',
            'Import text from a file or clear the editor instantly',
        ],
        'timeline': [
            ('Phase 01', 'Discovery', 'Teaching vs. Fixing',
             'Interviewed writers and found explanations mattered more than raw '
             'correction accuracy.'),
            ('Phase 02', 'Build', 'Detection & Scoring',
             'Built the issue detection pipeline and the 0–100 scoring model over it.'),
            ('Phase 03', 'Build', 'Explanation Engine',
             'Generated a short, specific rule explanation for every suggestion and '
             'wired up single and bulk fix application.'),
            ('Phase 04', 'Launch', 'Editor Polish',
             'Inline highlighting, review/edit toggle, copy-corrected and file import.'),
        ],
    },
    {
        'title': 'Finance Agent — Invoice & Document Intelligence',
        'subtitle': 'Upload invoices and statements, then ask questions about them',
        'category': 'data',
        'tags': 'Django, RAG, Document AI, OCR, Analytics',
        'image': 'projects/finance-agent.jpeg',
        'year': '2026',
        'description': (
            'A finance document agent that extracts invoices into structured, '
            'chartable data and reads statements, P&L and reports so you can query '
            'them in plain language.'
        ),
        'detailed_description': (
            'Finance Agent turns a folder of finance paperwork into something you can '
            'actually ask questions of. Drop in invoices, statements, P&L sheets or '
            'reports across six formats — PDF, image, XLSX, DOCX, CSV and Markdown — '
            'and the Extract & Store step converts them into structured records rather '
            'than a pile of text.\n\n'
            'Invoices become tabular data you can total, chart and reconcile. '
            'Statements and reports are indexed for retrieval, so questions like '
            '"What are the line items on invoice INV-2026-…?" or "What are the two '
            'open questions in the statement?" get answered against the actual '
            'documents, with the knowledge base carried across sessions.\n\n'
            'A persistent history sidebar keeps every past thread with its message '
            'count, and answers worth keeping can be saved. The interface is '
            'deliberately restrained — editorial serif, plenty of white space — '
            'because finance users read carefully.'
        ),
        'highlights': [
            ('chart', '6', 'File Formats Supported'),
            ('star', 'Q&A', 'Over Your Own Documents'),
            ('bolt', 'Auto', 'Invoice Extraction'),
            ('clock', 'Persistent', 'Session History'),
        ],
        'features': [
            'Upload PDF, image, XLSX, DOCX, CSV and Markdown documents',
            'Extract & Store converts invoices into structured, chartable data',
            'Natural-language Q&A over invoices, statements, P&L and reports',
            'Persistent knowledge base carried across sessions',
            'Separate invoice and finance-document libraries',
            'Full chat history sidebar with per-thread message counts',
            'Save any answer for later reference',
            'Suggested starter questions for new sessions',
        ],
        'timeline': [
            ('Phase 01', 'Discovery', 'Document Survey',
             'Collected real invoice and statement formats to scope what extraction '
             'had to handle.'),
            ('Phase 02', 'Build', 'Extraction Pipeline',
             'Built multi-format ingestion and the invoice-to-structured-data '
             'extractor with a stored knowledge base.'),
            ('Phase 03', 'Build', 'Retrieval & Q&A',
             'Added document retrieval, grounded answering, totals and charting over '
             'extracted records.'),
            ('Phase 04', 'Launch', 'Workspace UI',
             'History sidebar, saved answers, suggested questions and the editorial '
             'interface pass.'),
        ],
    },
    {
        'title': 'AI Gmail Sender',
        'subtitle': 'Describe the email in a sentence — the AI writes and sends it',
        'category': 'backend',
        'tags': 'Django, Gmail API, OAuth, LLM, Automation',
        'image': 'projects/ai-gmail-sender.jpeg',
        'year': '2026',
        'description': (
            'An email composer that takes a one-line description, drafts the full '
            'message and sends it through your connected Gmail account — with a mock '
            'mode so nothing goes out while you test.'
        ),
        'detailed_description': (
            'AI Gmail Sender collapses writing an email into two fields: who it goes '
            'to, and what you want to say. Describe the intent in plain language — '
            '"Send a polite follow-up email to my client about the project update" — '
            'and the AI composes the full message and delivers it through the Gmail '
            'API in one action.\n\n'
            'The safety design is the interesting part. A prominent Mock Mode composes '
            'the email exactly as it would in production but sends nothing, so the '
            'flow can be demonstrated and tested without touching a real inbox. '
            'Connection status is shown at all times, and the app never stores the '
            'content of your emails.\n\n'
            'Gmail connection is handled through a guided OAuth setup with an inline '
            'setup guide, so a non-technical user can get from install to first sent '
            'email without leaving the page.'
        ),
        'highlights': [
            ('bolt', '2', 'Fields to Send an Email'),
            ('star', 'Mock', 'Safe Testing Mode'),
            ('users', 'OAuth', 'Guided Gmail Setup'),
            ('clock', '1000', 'Character Prompt Limit'),
        ],
        'features': [
            'Natural-language email description with a 1000-character prompt',
            'AI composes and sends in a single action',
            'Mock Mode composes without sending, for safe testing',
            'Live connection status indicator',
            'Guided Gmail OAuth setup with an inline setup guide',
            'Recipient validation before sending',
            'Email content is never stored',
            'Contextual quick tips for better prompts',
        ],
        'timeline': [
            ('Phase 01', 'Discovery', 'Flow Design',
             'Reduced the compose-and-send journey to the smallest number of fields '
             'that still produced a usable email.'),
            ('Phase 02', 'Build', 'Gmail Integration',
             'Implemented Gmail OAuth, token handling and the send pipeline.'),
            ('Phase 03', 'Build', 'Generation & Mock Mode',
             'Built the AI composition layer and the mock send path used for testing '
             'and demos.'),
            ('Phase 04', 'Launch', 'Onboarding',
             'Setup guide, connection status, quick tips and the privacy pass.'),
        ],
    },
    {
        'title': 'NutriScan — AI Nutrition Analyzer',
        'subtitle': 'Describe your meal in a sentence, get the full macro breakdown',
        'category': 'ml',
        'tags': 'Django, LLM, Nutrition, Health Tech, Data Viz',
        'image': 'projects/nutriscan.jpeg',
        'year': '2026',
        'description': (
            'A nutrition tracker with no database lookup and no barcode scanning — '
            'describe what you ate in plain English and get a per-item calorie and '
            'macro breakdown.'
        ),
        'detailed_description': (
            'Food logging fails because it is tedious. NutriScan removes the search-'
            'and-select step entirely: type "I had 2 scrambled eggs cooked in butter, '
            '2 slices of brown toast with peanut butter, and a glass of whole milk" '
            'and it returns a full itemised breakdown.\n\n'
            'Each detected food becomes a row with its estimated quantity, calories, '
            'protein, carbs and fat — scrambled eggs at 140 kcal, butter at 102, brown '
            'toast at 160, peanut butter at 188, whole milk at 150. The summary rail '
            'totals it (740 kcal) and shows each macro both in grams and as a share of '
            'total calories, so the balance of a meal is visible at a glance rather '
            'than buried in numbers.\n\n'
            'The app is honest about its estimates — a standing note reminds users '
            'that portions are AI-estimated and that naming the cooking method '
            'improves fat accuracy. Analysed meals can be logged, revisited from '
            'History, saved to Favorites, or rolled up in Insights.'
        ),
        'highlights': [
            ('chart', '3', 'Macros Tracked Per Item'),
            ('bolt', '1', 'Sentence to Full Breakdown'),
            ('star', '%', 'Macro Share of Calories'),
            ('clock', 'Logged', 'History & Favorites'),
        ],
        'features': [
            'Natural-language meal description up to 500 characters',
            'Per-item table: quantity, calories, protein, carbs and fat',
            'Total calorie count with macro grams and percentage of calories',
            'Log any analysed meal to your history',
            'History, Favorites and Insights views',
            'AI note panel alongside the numeric summary',
            'Cooking-method hints for more accurate fat estimates',
            'Light and dark themes',
        ],
        'timeline': [
            ('Phase 01', 'Discovery', 'Why Food Logging Fails',
             'Studied drop-off in existing trackers and traced it to the search-and-'
             'select step.'),
            ('Phase 02', 'Build', 'Meal Parsing',
             'Built natural-language meal parsing into discrete food items with '
             'estimated portions.'),
            ('Phase 03', 'Build', 'Nutrition Engine',
             'Added calorie and macro estimation per item, meal totals and macro-share '
             'calculation.'),
            ('Phase 04', 'Launch', 'Tracking Layer',
             'History, favorites, insights, meal logging and the summary rail.'),
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed the six AI tool projects from the ProjectsHub screenshots.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace', action='store_true',
            help='Delete these six projects first, then recreate them.'
        )

    def handle(self, *args, **opts):
        titles = [p['title'] for p in PROJECTS]

        if opts['replace']:
            n, _ = Project.objects.filter(title__in=titles).delete()
            self.stdout.write(self.style.WARNING(f'Removed {n} existing rows.'))

        created = skipped = 0
        for i, data in enumerate(PROJECTS):
            if Project.objects.filter(title=data['title']).exists():
                self.stdout.write(f'  = exists, skipped: {data["title"]}')
                skipped += 1
                continue

            highlights = data.pop('highlights')
            features = data.pop('features')
            timeline = data.pop('timeline')

            p = Project.objects.create(
                is_active=True, show_on_index=True, order=i, **data
            )
            ProjectImage.objects.create(
                project=p, image=data['image'],
                caption=f'{p.title} — main interface',
                alt=f'Screenshot of the {p.title} interface', order=0,
            )
            for j, (icon, value, label) in enumerate(highlights):
                ProjectHighlight.objects.create(
                    project=p, icon=icon, value=value, label=label, order=j
                )
            for j, text in enumerate(features):
                ProjectFeature.objects.create(project=p, text=text, order=j)
            for j, (phase, date, title, desc) in enumerate(timeline):
                ProjectTimelinePhase.objects.create(
                    project=p, phase=phase, date=date,
                    title=title, desc=desc, order=j
                )

            self.stdout.write(self.style.SUCCESS(
                f'  + {p.title}  ({len(highlights)} highlights, '
                f'{len(features)} features, {len(timeline)} phases)'
            ))
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {created} created, {skipped} already present.'
        ))
        if created:
            self.stdout.write(
                'Still to fill in from the admin: price / price_label, project_url, '
                'github_url, case_study_url, youtube_url, role, duration, team_size.'
            )
