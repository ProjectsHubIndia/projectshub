import json
import re

from django.test import Client, TestCase
from django.urls import reverse

from core.models import (
    RoadmapGroup, RoadmapNode, RoadmapResource, RoadmapSettings, RoadmapTopic,
)
from core.roadmap_seed import import_roadmap, load_seed


def extract_json(html, element_id):
    match = re.search(
        r'<script id="%s" type="application/json">(.*?)</script>' % element_id,
        html, re.S,
    )
    assert match, 'json_script #%s not rendered' % element_id
    return json.loads(match.group(1))


class RoadmapModelTests(TestCase):
    def setUp(self):
        # The 0022 data migration already seeded the real roadmap, so these
        # tests use titles that do not appear in the shipped fixture.
        self.node = RoadmapNode.objects.create(number=90, title='Edge Inference Patterns')

    def test_slug_is_generated_from_title(self):
        self.assertEqual(self.node.slug, 'edge-inference-patterns')

    def test_duplicate_titles_get_distinct_slugs(self):
        other = RoadmapNode.objects.create(number=91, title='Edge Inference Patterns')
        self.assertEqual(other.slug, 'edge-inference-patterns-2')

    def test_topic_key_is_generated_from_label(self):
        topic = RoadmapTopic.objects.create(node=self.node, label='What is RAG?')
        self.assertEqual(topic.key, 'what-is-rag')

    def test_topic_title_falls_back_to_label(self):
        topic = RoadmapTopic.objects.create(node=self.node, label='Tokens')
        self.assertEqual(topic.display_title, 'Tokens')
        topic.title = 'Tokens & Tokenisation'
        self.assertEqual(topic.display_title, 'Tokens & Tokenisation')

    def test_topic_follows_its_group_to_the_right_chapter(self):
        other = RoadmapNode.objects.create(number=92, title='Edge Agent Runtime')
        group = RoadmapGroup.objects.create(node=other, title='Concepts')
        topic = RoadmapTopic.objects.create(node=self.node, group=group, label='Tools')
        self.assertEqual(topic.node_id, other.id)

    def test_resource_label_falls_back_to_type(self):
        topic = RoadmapTopic.objects.create(node=self.node, label='Tokens')
        resource = RoadmapResource.objects.create(
            topic=topic, tier='free', resource_type='video', title='Tokenisation explained'
        )
        self.assertEqual(resource.display_label, 'Video')
        resource.label = 'YouTube'
        self.assertEqual(resource.display_label, 'YouTube')

    def test_settings_is_a_singleton(self):
        first = RoadmapSettings.get_settings()
        self.assertEqual(RoadmapSettings.get_settings().pk, first.pk)
        self.assertEqual(RoadmapSettings.objects.count(), 1)


class RoadmapSeedTests(TestCase):
    def test_seed_fixture_imports_cleanly(self):
        counts = import_roadmap(
            RoadmapNode, RoadmapGroup, RoadmapTopic, RoadmapResource
        )
        self.assertEqual(counts['chapters'], 13)
        self.assertEqual(RoadmapNode.objects.count(), 13)
        self.assertEqual(RoadmapTopic.objects.count(), counts['topics'])
        self.assertGreater(counts['topics'], 120)

    def test_import_is_idempotent(self):
        import_roadmap(RoadmapNode, RoadmapGroup, RoadmapTopic, RoadmapResource)
        before = (
            RoadmapNode.objects.count(),
            RoadmapGroup.objects.count(),
            RoadmapTopic.objects.count(),
            RoadmapResource.objects.count(),
        )
        import_roadmap(RoadmapNode, RoadmapGroup, RoadmapTopic, RoadmapResource)
        after = (
            RoadmapNode.objects.count(),
            RoadmapGroup.objects.count(),
            RoadmapTopic.objects.count(),
            RoadmapResource.objects.count(),
        )
        self.assertEqual(before, after)

    def test_keep_resources_does_not_discard_admin_added_links(self):
        import_roadmap(RoadmapNode, RoadmapGroup, RoadmapTopic, RoadmapResource)
        topic = RoadmapTopic.objects.get(key='what_is_ai_eng')
        RoadmapResource.objects.create(
            topic=topic, tier='free', resource_type='article',
            title='Added by hand', url='https://example.com/',
        )
        count = topic.resources.count()

        import_roadmap(
            RoadmapNode, RoadmapGroup, RoadmapTopic, RoadmapResource,
            replace_resources=False,
        )
        self.assertEqual(topic.resources.count(), count)
        self.assertTrue(topic.resources.filter(title='Added by hand').exists())

    def test_seed_has_no_links_to_the_404ing_workshops_path(self):
        for chapter in load_seed():
            for topic in chapter['topics']:
                for resource in topic['resources']:
                    self.assertFalse(
                        resource['url'].startswith('/workshops'),
                        '%s still points at /workshops/' % resource['title'],
                    )

    def test_every_seeded_topic_key_is_unique(self):
        keys = [t['key'] for c in load_seed() for t in c['topics']]
        self.assertEqual(len(keys), len(set(keys)))


class RoadmapViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        import_roadmap(RoadmapNode, RoadmapGroup, RoadmapTopic, RoadmapResource)

    def setUp(self):
        self.client = Client()
        self.url = reverse('ai_roadmap')

    def test_page_renders_every_active_chapter_and_topic(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertEqual(html.count('class="timeline-item"'), RoadmapNode.objects.count())
        self.assertEqual(
            html.count('class="tag" data-topic='), RoadmapTopic.objects.count()
        )

    def test_topics_are_published_as_json_for_the_drawer(self):
        html = self.client.get(self.url).content.decode()
        topics = extract_json(html, 'roadmapTopicsData')
        self.assertEqual(len(topics), RoadmapTopic.objects.count())

        entry = topics['what_is_ai_eng']
        self.assertEqual(entry['title'], 'What is an AI Engineer?')
        self.assertEqual(entry['chapter'], '1. Introduction')
        self.assertTrue(entry['free'])

    def test_inactive_rows_are_left_out(self):
        topic = RoadmapTopic.objects.get(key='what_is_ai_eng')
        topic.is_active = False
        topic.save()

        html = self.client.get(self.url).content.decode()
        self.assertNotIn('data-topic="what_is_ai_eng"', html)
        self.assertNotIn('what_is_ai_eng', extract_json(html, 'roadmapTopicsData'))

    def test_inactive_resource_is_not_published(self):
        topic = RoadmapTopic.objects.get(key='what_is_ai_eng')
        resource = topic.resources.filter(tier='free').first()
        resource.is_active = False
        resource.save()

        topics = extract_json(self.client.get(self.url).content.decode(), 'roadmapTopicsData')
        titles = [r['title'] for r in topics['what_is_ai_eng']['free']]
        self.assertNotIn(resource.title, titles)

    def test_inactive_chapter_drops_its_topics_too(self):
        node = RoadmapNode.objects.get(number=1)
        node.is_active = False
        node.save()

        html = self.client.get(self.url).content.decode()
        self.assertEqual(html.count('class="timeline-item"'), RoadmapNode.objects.count() - 1)
        self.assertNotIn('what_is_ai_eng', extract_json(html, 'roadmapTopicsData'))

    def test_cta_label_and_url_come_from_settings(self):
        config = RoadmapSettings.get_settings()
        config.cta_label = 'Browse ML Builds'
        config.cta_url = '/projects/?category=data'
        config.save()

        html = self.client.get(self.url).content.decode()
        self.assertIn('Browse ML Builds', html)
        self.assertIn('/projects/?category=data', html)

    def test_cta_url_resolves_on_this_site(self):
        config = RoadmapSettings.get_settings()
        self.assertEqual(self.client.get(config.cta_url).status_code, 200)
        self.assertEqual(self.client.get(config.workshop_url).status_code, 200)

    def test_drawer_side_is_driven_by_settings(self):
        html = self.client.get(self.url).content.decode()
        self.assertIn('roadmap-modal--left', html)

        config = RoadmapSettings.get_settings()
        config.drawer_side = 'right'
        config.save()

        html = self.client.get(self.url).content.decode()
        self.assertIn('roadmap-modal--right', html)
        self.assertNotIn('roadmap-modal--left', html)

    def test_hero_copy_comes_from_settings(self):
        config = RoadmapSettings.get_settings()
        config.hero_title_prefix = 'Become an'
        config.hero_title_highlight = 'AI Builder'
        config.hero_subtitle = 'Ship production AI in 2026'
        config.save()

        html = self.client.get(self.url).content.decode()
        self.assertIn('Become an', html)
        self.assertIn('AI Builder', html)
        self.assertIn('Ship production AI in 2026', html)

    def test_layout_switches_hide_the_stepper_and_badge(self):
        config = RoadmapSettings.get_settings()
        config.show_stepper = False
        config.show_progress_badge = False
        config.save()

        html = self.client.get(self.url).content.decode()
        self.assertNotIn('id="stepperContainer"', html)
        self.assertNotIn('id="timelineProgressBadge"', html)

    def test_fallback_urls_are_exposed_to_the_client(self):
        config = extract_json(
            self.client.get(self.url).content.decode(), 'roadmapConfigData'
        )
        self.assertEqual(config['drawerSide'], 'left')
        self.assertEqual(config['workshopUrl'], '/workshop/')

    def test_page_still_renders_with_an_empty_roadmap(self):
        RoadmapNode.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('roadmap-empty', response.content.decode())

    def test_no_legacy_inline_onclick_handlers_remain(self):
        html = self.client.get(self.url).content.decode()
        self.assertNotIn('openDrawer(', html)
