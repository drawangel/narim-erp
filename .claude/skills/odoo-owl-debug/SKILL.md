---
name: odoo-owl-debug
description: Debugging workflow for Odoo 18 OWL components, assets, and template extensions. This skill should be used when OWL components don't appear, JavaScript assets fail to load, template extensions don't work, or there are 500 errors in asset bundles. Covers SearchPanel, FormView, ListView extensions and common pitfalls.
---

# Odoo 18 OWL Debugging Skill

Structured debugging workflow for Odoo 18 OWL frontend issues.

## When to Use This Skill

- OWL component not appearing in UI
- JavaScript assets not loading in bundle
- Template extension (t-inherit) not working
- 500 errors on asset bundle requests
- Patches not being applied to components

## Quick Diagnostic Checklist

When an OWL component doesn't appear, verify in this order:

### 1. Assets Loading

Create a minimal debug file to verify assets load:

```javascript
/** @odoo-module **/
console.log("=== MODULE_NAME JS LOADED ===");
```

Add to manifest and check browser console. If message appears, assets work.

### 2. Patch Application

Add console.log inside patch to verify it executes:

```javascript
patch(Component.prototype, {
    setup() {
        super.setup(...arguments);
        console.log("=== PATCH APPLIED ===", { model: this.env.searchModel?.resModel });
    }
});
```

### 3. Template Extension

If patch works but UI doesn't appear, the template extension is wrong. See "Template Extension Patterns" below.

## Common Causes of Failure

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| No console.log at all | Assets not in bundle | Verify manifest, update module, restart |
| Patch logs but no UI | Wrong template to extend | Check template chain, extend correct one |
| 500 on assets | Syntax error in JS/XML | Check logs, validate syntax |
| Works then breaks | Cache issue | `?debug=assets` + Ctrl+Shift+R |

## Template Extension Patterns

### SearchPanel (Critical Knowledge)

The SearchPanel template chain is:

```
web.SearchPanel (entry point)
  → web.SearchPanel.Regular (desktop, calls SearchPanelContent)
  → web.SearchPanel.Small (mobile)
  → web.SearchPanel.Sidebar (collapsed)

web.SearchPanelContent (the actual content)
  ← web.SearchPanel.Regular inherits from this (t-inherit-mode="primary")
```

**CRITICAL**: To add content to SearchPanel:
- Extend `web.SearchPanel.Regular`, NOT `web.SearchPanelContent`
- The `.Regular` template is what actually renders on desktop
- Extensions to `.Content` don't propagate because `.Regular` uses `primary` mode

**Working pattern:**

```xml
<t t-name="mymodule.SearchPanelExtension"
   t-inherit="web.SearchPanel.Regular"
   t-inherit-mode="extension">
    <xpath expr="//section[@t-foreach='sections']" position="before">
        <section t-if="showMySection" class="o_search_panel_section">
            <!-- content -->
        </section>
    </xpath>
</t>
```

### XPath Pitfalls

**Never target elements with t-if that may not exist:**

```xml
<!-- BAD: Element doesn't exist when condition is false -->
<xpath expr="//div[@class='o_search_panel_empty_state']" position="after">

<!-- GOOD: Target stable elements -->
<xpath expr="//section[@t-foreach='sections']" position="before">
```

### Adding Components to Existing Components

```javascript
import { SearchPanel } from "@web/search/search_panel/search_panel";
import { patch } from "@web/core/utils/patch";

// 1. Add component to target's components
SearchPanel.components = { ...SearchPanel.components, MyComponent };

// 2. Patch prototype for state/props
patch(SearchPanel.prototype, {
    setup() {
        super.setup(...arguments);
        this.showMyComponent = true;
    }
});
```

## Asset Bundle Debugging

### Verify Module State

```bash
docker compose exec odoo python -c "
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
db = 'narim'
registry = Registry(db)
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    mod = env['ir.module.module'].search([('name', '=', 'MODULE_NAME')])
    print(f'State: {mod.state}')
"
```

If state is "uninstalled", force install:
```bash
docker compose exec odoo python -m odoo -d narim -i MODULE_NAME --stop-after-init
```

### Force Asset Regeneration

```bash
# 1. Update module
docker compose exec odoo python -m odoo -d narim -u MODULE_NAME --stop-after-init

# 2. Restart Odoo
docker compose restart odoo

# 3. In browser: add ?debug=assets to URL

# 4. Hard refresh: Ctrl+Shift+R
```

## Debugging Workflow Summary

```
1. Create debug_test.js with console.log
   ↓ (if no log appears)
   → Check manifest, module state, restart

2. Add console.log to patch
   ↓ (if patch doesn't log)
   → Check import paths, verify component name

3. Patch logs but no UI
   ↓
   → Wrong template. Check template chain.
   → For SearchPanel: extend .Regular not .Content

4. UI appears then 500 error
   ↓
   → Cache issue. Update module + restart + ?debug=assets + Ctrl+Shift+R
```

## Key Odoo 18 OWL Facts

- `ir.asset` table is EMPTY in dev mode - assets load from manifests at runtime
- Templates: `t-inherit-mode="extension"` for global changes, `"primary"` for new variants
- Luxon is global: `const { DateTime } = luxon;` (no import needed)
- SearchModel API: `this.env.searchModel.createNewFilters([{description, domain, type: "filter"}])`
- Prefer explicit asset paths in manifest over globs for easier debugging
