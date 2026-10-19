"""Optional Chromium UI test; uses in-memory HTML to avoid navigation policies.

python tests/browser_smoke.py  # Requires playwright and a local Chromium installation
"""
from pathlib import Path
import re
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]/'site'
html=(root/'index.html').read_text(encoding='utf-8')
html=re.sub(r'<link rel="stylesheet"[^>]+>','',html)
html=re.sub(r'<script src="assets/[^>]+></script>','',html)
with sync_playwright() as p:
    for width,height in [(1440,900),(390,844)]:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':width,'height':height})
        errors=[]
        page.on('pageerror', lambda e:errors.append(str(e)))
        page.set_content(html)
        page.add_style_tag(content=(root/'assets/style.css').read_text(encoding='utf-8'))
        for file in ['data.js','india-map.js','app.js']:
            page.add_script_tag(content=(root/'assets'/file).read_text(encoding='utf-8'))
        assert page.locator('.metric').count()>=4
        assert page.locator('#airportMap circle').count()>80
        for section in ['overview','explorer','models','method']:
            page.locator(f'[data-page="{section}"]').click()
            assert page.locator(f'#page-{section}').is_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.locator('[data-page="models"]').click()
        page.locator('[data-ml-tab="classification"]').click()
        assert page.locator('#confusionMatrix button').count()==4
        page.locator('[data-ml-tab="clustering"]').click()
        assert page.locator('#pcaChart circle').count()>100
        page.locator('[data-page="explorer"]').click()
        page.locator('#airportSearch').fill('COK')
        assert page.locator('#airportRows tr').count()==1
        page.locator('#airportSearch').fill('')
        page.locator('#exploreYear').select_option('2024')
        assert '2024' in page.locator('#tableSubtitle').inner_text()
        assert not errors,errors
        browser.close()
    print('PASS: desktop, mobile, navigation, map, year, search and no runtime errors')
