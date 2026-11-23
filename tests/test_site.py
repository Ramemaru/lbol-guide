import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

import build


class SiteBuildTests(unittest.TestCase):
    def test_admin_config_matches_articles(self):
        config = yaml.safe_load((build.ROOT / 'admin/config.yml').read_text(encoding='utf-8'))
        self.assertEqual(config['backend']['name'], 'github')
        self.assertEqual(config['backend']['branch'], 'main')
        self.assertTrue(config['local_backend'])
        self.assertEqual(config['locale'], 'ja')
        self.assertEqual(config['media_folder'], 'assets/uploads')
        self.assertEqual([c['name'] for c in config['collections']], ['cards', 'bosses', 'characters'])
        for collection in config['collections']:
            self.assertTrue(collection['create'])
            self.assertEqual(collection['slug'], '{{fields.slug}}')
            fields = {field['name']: field for field in collection['fields']}
            for required in ['title', 'slug', 'summary', 'tags', 'status', 'draft', 'sample', 'body', 'image']:
                self.assertIn(required, fields)
            self.assertTrue(fields['draft']['default'])

    def test_local_markdown_links_and_media_are_correct(self):
        text = '''<p><img src="/assets/uploads/illustration.png" alt=""></p>\n<p><a href="/bosses/example-boss/#section-1">ボス</a></p>'''
        localized = build.localize_article_links(text)
        self.assertIn('src="../../assets/uploads/illustration.png"', localized)
        self.assertIn('href="../../bosses/example-boss/index.html#section-1"', localized)
        self.assertEqual(build.normalize_image('/assets/uploads/p.png'), 'assets/uploads/p.png')

    def test_builds_with_cms_style_article_and_hides_drafts(self):
        card_file = build.ROOT / 'content/cards/test-cms-entry.md'
        boss_file = build.ROOT / 'content/bosses/test-cms-draft.md'
        self.addCleanup(lambda: card_file.unlink(missing_ok=True))
        self.addCleanup(lambda: boss_file.unlink(missing_ok=True))
        card_file.write_text('''---
title: "検証用カード"
slug: test-cms-entry
summary: "概要"
status: "有力"
tags: [検証]
draft: false
image: "/assets/uploads/illustration.png"
updated: null
---

## 結論

![カードの画像](/assets/uploads/illustration.png)

[関連ボス](/bosses/example-boss/)
''', encoding='utf-8')
        boss_file.write_text('''---
title: "検証用ボス"
slug: test-cms-draft
draft: true
---
## 内容
''', encoding='utf-8')
        build.main()
        html = (build.OUTPUT / 'cards/test-cms-entry/index.html').read_text(encoding='utf-8')
        self.assertIn('../../assets/uploads/illustration.png', html)
        self.assertIn('../../bosses/example-boss/index.html', html)
        self.assertIn('検証用カード', html)
        self.assertNotIn('<dd>None</dd>', html)
        self.assertFalse((build.OUTPUT / 'bosses/test-cms-draft').exists())
        self.assertTrue((build.OUTPUT / 'admin/config.yml').exists())
        self.assertTrue((build.OUTPUT / 'admin/index.html').exists())
        self.assertTrue((build.OUTPUT / 'assets/style.css').exists())
        index = json.loads((build.OUTPUT / 'search-index.json').read_text(encoding='utf-8'))
        self.assertTrue(any(x['url'] == '/cards/test-cms-entry/' for x in index))
        self.assertFalse(any(x['url'] == '/bosses/test-cms-draft/' for x in index))

    def test_slug_and_filename_must_stay_in_sync(self):
        with tempfile.TemporaryDirectory(dir=build.ROOT) as tmp:
            path=Path(tmp) / 'old-name.md'
            path.write_text('---\ntitle: "例"\nslug: new-name\n---\n本文', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'does not match filename'):
                build.load_article(path, 'cards')


if __name__ == '__main__':
    unittest.main()
