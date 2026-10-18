from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    page.goto('http://127.0.0.1:9000/')
    page.wait_for_load_state('networkidle')
    page.evaluate("() => { window.confirm = () => true; const m = document.getElementById('releaseNotesModal'); if (m) m.remove(); }")
    page.locator('#modeDropdownBtn').click()
    page.wait_for_timeout(300)
    page.locator('[data-action="toggle-multi-switch"]').click()
    page.wait_for_timeout(1000)
    page.evaluate("() => { window.confirm = () => true; const btn = document.querySelector('div[data-template-id=\"vpc_core_leaf\"] button.template-action'); if (btn) btn.click(); }")
    page.wait_for_timeout(2500)
    page.locator('button:has-text("Customize Network")').click()
    page.wait_for_timeout(1500)
    result = page.evaluate("""() => {
        const editor = document.getElementById('configurationEditor');
        const panel = document.getElementById('panel-switches');
        const list = document.getElementById('switchesList');
        const item = list ? list.querySelector('.switch-item') : null;
        const btn = item ? item.querySelector('button') : null;
        const cp = document.querySelector('.config-panels');
        const pc = document.querySelector('.panel-content');
        return {
            editorH: editor ? editor.getBoundingClientRect().height : 'MISSING',
            panelClasses: panel ? panel.className : 'MISSING',
            listH: list ? list.getBoundingClientRect().height : 'MISSING',
            itemH: item ? item.getBoundingClientRect().height : 'MISSING',
            btnH: btn ? btn.getBoundingClientRect().height : 'MISSING',
            btnTop: btn ? btn.getBoundingClientRect().top : 'MISSING',
            btnBottom: btn ? btn.getBoundingClientRect().bottom : 'MISSING',
            configPanelsH: cp ? cp.getBoundingClientRect().height : 'MISSING',
            configPanelsOverflow: cp ? window.getComputedStyle(cp).overflow : 'MISSING',
            panelContentH: pc ? pc.getBoundingClientRect().height : 'MISSING',
            panelContentOverflow: pc ? window.getComputedStyle(pc).overflow : 'MISSING',
            panelContentMaxH: pc ? window.getComputedStyle(pc).maxHeight : 'MISSING',
            switchesListOverflow: list ? window.getComputedStyle(list).overflow : 'MISSING',
            step1Classes: document.getElementById('step-1') ? document.getElementById('step-1').className : 'MISSING',
        };
    }""")
    print("=== DIAGNOSTIC ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
    b.close()
