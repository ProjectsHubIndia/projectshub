from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    RoadmapGroup, RoadmapNode, RoadmapResource, RoadmapSettings, RoadmapTopic,
)
from core.roadmap_seed import SEED_PATH, import_roadmap, load_seed


class Command(BaseCommand):
    help = (
        'Load (or refresh) the AI Engineer Roadmap chapters, sub-sections, '
        'topics and resources from core/fixtures/ai_roadmap_seed.json.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', dest='path', default=SEED_PATH,
            help='Seed JSON to import. Defaults to the bundled fixture.',
        )
        parser.add_argument(
            '--keep-resources', action='store_true',
            help='Do not replace resource links on topics that already have them.',
        )
        parser.add_argument(
            '--flush', action='store_true',
            help='Delete every existing roadmap chapter first (cascades to topics).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['flush']:
            deleted = RoadmapNode.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'Flushed {deleted} roadmap rows.'))

        chapters = load_seed(options['path'])
        counts = import_roadmap(
            RoadmapNode, RoadmapGroup, RoadmapTopic, RoadmapResource,
            chapters=chapters,
            replace_resources=not options['keep_resources'],
        )
        RoadmapSettings.get_settings()

        self.stdout.write(self.style.SUCCESS(
            'Imported {chapters} chapters, {groups} sub-sections, '
            '{topics} topics, {resources} resources.'.format(**counts)
        ))
