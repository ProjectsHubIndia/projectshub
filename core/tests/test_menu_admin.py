"""Tests for the menu management models, admin, and preview view.

Focus is on the failure modes the admin could previously save: parent cycles
(which made depth walking non-terminating), cross-menu parents, and the
hardcoded admin URLs.
"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from core.models import Menu, MenuConfig, MenuItem


class MenuItemDepthTests(TestCase):
    def setUp(self):
        self.menu = Menu.objects.create(name='Header Menu')

    def test_depth_counts_nesting_levels(self):
        root = MenuItem.objects.create(menu=self.menu, label='Work', destination='/work/')
        child = MenuItem.objects.create(
            menu=self.menu, label='Projects', destination='/projects/', parent=root
        )
        grandchild = MenuItem.objects.create(
            menu=self.menu, label='AI', destination='/projects/ai/', parent=child
        )

        self.assertEqual(root.get_depth(), 0)
        self.assertEqual(child.get_depth(), 1)
        self.assertEqual(grandchild.get_depth(), 2)

    def test_get_depth_terminates_on_self_referencing_cycle(self):
        """A row pointing at itself must not loop forever.

        Rows like this can exist from before clean() was added, so get_depth
        has to tolerate them rather than hang the request.
        """
        item = MenuItem.objects.create(menu=self.menu, label='Loop', destination='/loop/')
        MenuItem.objects.filter(pk=item.pk).update(parent=item.pk)
        item.refresh_from_db()

        self.assertEqual(item.get_depth(), 0)

    def test_get_depth_terminates_on_two_node_cycle(self):
        a = MenuItem.objects.create(menu=self.menu, label='A', destination='/a/')
        b = MenuItem.objects.create(menu=self.menu, label='B', destination='/b/', parent=a)
        # Close the loop behind validation's back: a -> b -> a.
        MenuItem.objects.filter(pk=a.pk).update(parent=b.pk)

        self.assertLessEqual(MenuItem.objects.get(pk=a.pk).get_depth(), 10)


class MenuItemValidationTests(TestCase):
    def setUp(self):
        self.menu = Menu.objects.create(name='Header Menu')
        self.other_menu = Menu.objects.create(name='Footer Menu')

    def test_item_cannot_be_its_own_parent(self):
        item = MenuItem.objects.create(menu=self.menu, label='Work', destination='/work/')
        item.parent = item

        with self.assertRaises(ValidationError) as ctx:
            item.full_clean()
        self.assertIn('parent', ctx.exception.message_dict)

    def test_parent_must_be_in_the_same_menu(self):
        foreign = MenuItem.objects.create(
            menu=self.other_menu, label='Legal', destination='/legal/'
        )
        item = MenuItem(
            menu=self.menu, label='Work', destination='/work/', parent=foreign
        )

        with self.assertRaises(ValidationError) as ctx:
            item.full_clean()
        self.assertIn('parent', ctx.exception.message_dict)

    def test_cannot_nest_under_own_descendant(self):
        root = MenuItem.objects.create(menu=self.menu, label='Work', destination='/work/')
        child = MenuItem.objects.create(
            menu=self.menu, label='Projects', destination='/projects/', parent=root
        )
        root.parent = child

        with self.assertRaises(ValidationError) as ctx:
            root.full_clean()
        self.assertIn('parent', ctx.exception.message_dict)

    def test_valid_nesting_passes(self):
        root = MenuItem.objects.create(menu=self.menu, label='Work', destination='/work/')
        child = MenuItem(
            menu=self.menu, label='Projects', destination='/projects/', parent=root
        )

        child.full_clean()  # must not raise

    def test_nesting_beyond_max_depth_is_rejected(self):
        parent = None
        for i in range(MenuItem.MAX_DEPTH):
            parent = MenuItem.objects.create(
                menu=self.menu, label=f'Level {i}', destination=f'/l{i}/', parent=parent
            )

        too_deep = MenuItem(
            menu=self.menu, label='Too deep', destination='/deep/', parent=parent
        )
        with self.assertRaises(ValidationError) as ctx:
            too_deep.full_clean()
        self.assertIn('parent', ctx.exception.message_dict)


class MenuAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            'menuadmin', 'menuadmin@example.com', 'pw-for-tests'
        )
        self.client.force_login(self.user)
        self.menu = Menu.objects.create(name='Header Menu')

    def test_changelist_renders_with_preview_link(self):
        MenuItem.objects.create(menu=self.menu, label='Work', destination='/work/')
        response = self.client.get(reverse('admin:core_menu_changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, reverse('admin_menu_preview', args=[self.menu.pk])
        )

    def test_changelist_survives_a_parent_cycle(self):
        """The item changelist renders depth for every row.

        With an unguarded ancestor walk a cycle in the data hung this page.
        """
        a = MenuItem.objects.create(menu=self.menu, label='A', destination='/a/')
        b = MenuItem.objects.create(menu=self.menu, label='B', destination='/b/', parent=a)
        MenuItem.objects.filter(pk=a.pk).update(parent=b.pk)

        response = self.client.get(reverse('admin:core_menuitem_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_change_form_renders(self):
        response = self.client.get(
            reverse('admin:core_menu_change', args=[self.menu.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'menu-admin')

    def test_menuconfig_changelist_creates_and_redirects_to_singleton(self):
        self.assertFalse(MenuConfig.objects.exists())

        response = self.client.get(reverse('admin:core_menuconfig_changelist'))

        self.assertEqual(MenuConfig.objects.count(), 1)
        config = MenuConfig.objects.get()
        self.assertRedirects(
            response, reverse('admin:core_menuconfig_change', args=[config.pk])
        )

    def test_menuconfig_renders_radiolist_for_style_previews(self):
        """The change form's style mockups hook onto .radiolist.

        Without radio_fields the fields render as plain selects and the whole
        preview block is unreachable.
        """
        config = MenuConfig.get_config()
        response = self.client.get(
            reverse('admin:core_menuconfig_change', args=[config.pk])
        )
        self.assertContains(response, 'radiolist')

    def test_duplicate_menu_action_preserves_nesting(self):
        root = MenuItem.objects.create(menu=self.menu, label='Work', destination='/work/')
        MenuItem.objects.create(
            menu=self.menu, label='Projects', destination='/projects/', parent=root
        )

        response = self.client.post(
            reverse('admin:core_menu_changelist'),
            {'action': 'duplicate_menu', '_selected_action': [str(self.menu.pk)]},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        copy = Menu.objects.get(name='Header Menu (Copy)')
        self.assertEqual(copy.items.count(), 2)

        copied_child = copy.items.get(label='Projects')
        self.assertIsNotNone(copied_child.parent)
        # The parent must be the copy's own root, not the original's.
        self.assertEqual(copied_child.parent.menu_id, copy.pk)
        self.assertEqual(copied_child.parent.label, 'Work')

    def test_export_menu_json_returns_nested_structure(self):
        root = MenuItem.objects.create(menu=self.menu, label='Work', destination='/work/')
        MenuItem.objects.create(
            menu=self.menu, label='Projects', destination='/projects/', parent=root
        )

        response = self.client.post(
            reverse('admin:core_menu_changelist'),
            {'action': 'export_menu_json', '_selected_action': [str(self.menu.pk)]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response['Content-Disposition'])
        payload = response.json()
        items = payload['menus'][0]['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['children'][0]['label'], 'Projects')


class MenuPreviewViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            'previewadmin', 'previewadmin@example.com', 'pw-for-tests'
        )
        self.client.force_login(self.user)
        self.menu = Menu.objects.create(name='Header Menu')

    def test_preview_renders_nested_items(self):
        root = MenuItem.objects.create(menu=self.menu, label='Work', destination='/work/')
        MenuItem.objects.create(
            menu=self.menu, label='Projects', destination='/projects/', parent=root
        )

        response = self.client.get(reverse('admin_menu_preview', args=[self.menu.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Work')
        self.assertContains(response, 'Projects')
        # The class the style switcher keys off must be present.
        self.assertContains(response, 'menu-item-preview')
        self.assertContains(response, 'menu-preview-sublist')

    def test_preview_excludes_inactive_items(self):
        MenuItem.objects.create(
            menu=self.menu, label='Hidden', destination='/hidden/', is_active=False
        )
        response = self.client.get(reverse('admin_menu_preview', args=[self.menu.pk]))
        self.assertNotContains(response, 'Hidden')

    def test_preview_survives_a_parent_cycle(self):
        a = MenuItem.objects.create(menu=self.menu, label='A', destination='/a/')
        b = MenuItem.objects.create(menu=self.menu, label='B', destination='/b/', parent=a)
        MenuItem.objects.filter(pk=a.pk).update(parent=b.pk)

        response = self.client.get(reverse('admin_menu_preview', args=[self.menu.pk]))
        self.assertEqual(response.status_code, 200)

    def test_preview_requires_staff(self):
        self.client.logout()
        response = self.client.get(reverse('admin_menu_preview', args=[self.menu.pk]))
        self.assertEqual(response.status_code, 302)

    def test_preview_query_count_does_not_grow_with_items(self):
        """The tree is built from a single query over the menu's rows.

        The old recursive version issued a query per node plus one per ancestor
        for depth, so the count scaled with the menu. Comparing a small menu to
        a large one proves that independence without pinning a magic number.
        """
        url = reverse('admin_menu_preview', args=[self.menu.pk])
        root = MenuItem.objects.create(menu=self.menu, label='Root', destination='/r/')
        child = MenuItem.objects.create(
            menu=self.menu, label='Child', destination='/c/', parent=root
        )
        for i in range(20):
            MenuItem.objects.create(
                menu=self.menu, label=f'Leaf {i}', destination=f'/l{i}/', parent=child
            )

        with CaptureQueriesContext(connection) as captured:
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        item_queries = [
            q['sql'] for q in captured.captured_queries
            if 'core_menuitem' in q['sql']
        ]
        self.assertEqual(
            len(item_queries), 1,
            f'expected one query for the menu tree, got {len(item_queries)}',
        )


class MenuAdminSidebarTests(TestCase):
    def test_menu_models_appear_in_grouped_sidebar(self):
        """Menu and MenuConfig must be reachable from the curated sidebar.

        Models missing from GROUPS fall into the "Advanced records" bucket,
        where the menu editor was effectively hidden.
        """
        from core.templatetags.admin_menu import GROUPS

        grouped = {name for _, _, names in GROUPS for name in names}
        self.assertIn('Menu', grouped)
        self.assertIn('MenuConfig', grouped)
