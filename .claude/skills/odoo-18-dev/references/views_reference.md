# Odoo 18 Views Reference

## View Types Overview

| Type | Purpose | Common Use |
|------|---------|------------|
| `form` | Single record editing | Detail/edit pages |
| `list` (tree) | Multiple records table | List views |
| `kanban` | Card-based display | Visual workflows |
| `search` | Filtering options | Search bars |
| `calendar` | Date-based display | Scheduling |
| `graph` | Charts and graphs | Analytics |
| `pivot` | Pivot tables | Analysis |
| `gantt` | Timeline view | Project planning |
| `activity` | Activity scheduling | Tasks |

## Form View

```xml
<record id="my_model_view_form" model="ir.ui.view">
    <field name="name">my.model.view.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form string="My Model">
            <!-- Header with status bar and buttons -->
            <header>
                <button name="action_confirm" type="object"
                        string="Confirm" class="btn-primary"
                        invisible="state != 'draft'"/>
                <button name="action_cancel" type="object"
                        string="Cancel" invisible="state == 'cancelled'"/>
                <field name="state" widget="statusbar"
                       statusbar_visible="draft,confirmed,done"/>
            </header>

            <!-- Sheet for main content -->
            <sheet>
                <!-- Ribbon for special states -->
                <widget name="web_ribbon" title="Archived"
                        bg_color="bg-danger" invisible="active"/>

                <!-- Title area -->
                <div class="oe_title">
                    <label for="name"/>
                    <h1>
                        <field name="name" placeholder="Name..."/>
                    </h1>
                </div>

                <!-- Groups for field layout -->
                <group>
                    <group string="General">
                        <field name="partner_id"/>
                        <field name="date"/>
                        <field name="amount"/>
                    </group>
                    <group string="Details">
                        <field name="description"/>
                        <field name="category_id"/>
                    </group>
                </group>

                <!-- Notebook for tabs -->
                <notebook>
                    <page string="Lines" name="lines">
                        <field name="line_ids">
                            <list editable="bottom">
                                <field name="product_id"/>
                                <field name="quantity"/>
                                <field name="price"/>
                                <field name="subtotal"/>
                            </list>
                        </field>
                    </page>
                    <page string="Notes" name="notes">
                        <field name="notes" placeholder="Internal notes..."/>
                    </page>
                </notebook>
            </sheet>

            <!-- Chatter -->
            <chatter/>
        </form>
    </field>
</record>
```

## List (Tree) View

```xml
<record id="my_model_view_list" model="ir.ui.view">
    <field name="name">my.model.view.list</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <list string="My Models"
              default_order="date desc"
              decoration-danger="state == 'cancelled'"
              decoration-success="state == 'done'"
              decoration-info="state == 'draft'"
              multi_edit="1">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="date"/>
            <field name="amount" sum="Total"/>
            <field name="state"
                   decoration-success="state == 'done'"
                   decoration-warning="state == 'draft'"
                   widget="badge"/>
            <field name="company_id" groups="base.group_multi_company"/>
        </list>
    </field>
</record>
```

### List Attributes

| Attribute | Description |
|-----------|-------------|
| `editable="bottom/top"` | Inline editing |
| `default_order` | Default sort |
| `decoration-*` | Row coloring (danger, warning, success, info, muted) |
| `multi_edit="1"` | Enable multi-record editing |
| `limit` | Records per page |
| `groups_limit` | Groups per page |

## Kanban View

```xml
<record id="my_model_view_kanban" model="ir.ui.view">
    <field name="name">my.model.view.kanban</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state"
                class="o_kanban_small_column"
                quick_create="true"
                group_create="true"
                records_draggable="true">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="color"/>
            <field name="state"/>
            <progressbar field="state"
                         colors='{"draft": "secondary", "confirmed": "warning", "done": "success"}'/>
            <templates>
                <t t-name="card">
                    <div t-attf-class="#{kanban_color(record.color.raw_value)}">
                        <field name="name" class="fw-bold"/>
                        <field name="partner_id"/>
                        <div class="o_kanban_record_bottom">
                            <field name="date"/>
                            <field name="amount" widget="monetary"/>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

## Search View

```xml
<record id="my_model_view_search" model="ir.ui.view">
    <field name="name">my.model.view.search</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <search string="Search My Model">
            <!-- Search fields -->
            <field name="name" string="Name"
                   filter_domain="['|', ('name', 'ilike', self), ('reference', 'ilike', self)]"/>
            <field name="partner_id"/>
            <field name="category_id"/>

            <!-- Separator -->
            <separator/>

            <!-- Filters -->
            <filter name="filter_draft" string="Draft"
                    domain="[('state', '=', 'draft')]"/>
            <filter name="filter_confirmed" string="Confirmed"
                    domain="[('state', '=', 'confirmed')]"/>
            <separator/>
            <filter name="filter_my" string="My Records"
                    domain="[('user_id', '=', uid)]"/>
            <filter name="filter_today" string="Today"
                    domain="[('date', '=', context_today().strftime('%Y-%m-%d'))]"/>
            <separator/>
            <filter name="filter_archived" string="Archived"
                    domain="[('active', '=', False)]"/>

            <!-- Group by -->
            <group expand="0" string="Group By">
                <filter name="group_state" string="State"
                        context="{'group_by': 'state'}"/>
                <filter name="group_partner" string="Partner"
                        context="{'group_by': 'partner_id'}"/>
                <filter name="group_date" string="Date"
                        context="{'group_by': 'date:month'}"/>
            </group>

            <!-- Searchpanel (left sidebar) -->
            <searchpanel>
                <field name="category_id" icon="fa-folder"/>
                <field name="state" select="multi" icon="fa-tasks"/>
            </searchpanel>
        </search>
    </field>
</record>
```

## Calendar View

```xml
<record id="my_model_view_calendar" model="ir.ui.view">
    <field name="name">my.model.view.calendar</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <calendar string="My Calendar"
                  date_start="date_start"
                  date_stop="date_stop"
                  date_delay="duration"
                  color="partner_id"
                  mode="month"
                  quick_create="false"
                  event_open_popup="true">
            <field name="name"/>
            <field name="partner_id" filters="1"/>
            <field name="state"/>
        </calendar>
    </field>
</record>
```

## Graph View

```xml
<record id="my_model_view_graph" model="ir.ui.view">
    <field name="name">my.model.view.graph</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <graph string="My Analysis" type="bar" stacked="true">
            <field name="date" interval="month" type="row"/>
            <field name="category_id" type="col"/>
            <field name="amount" type="measure"/>
        </graph>
    </field>
</record>
```

## Pivot View

```xml
<record id="my_model_view_pivot" model="ir.ui.view">
    <field name="name">my.model.view.pivot</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <pivot string="My Analysis" display_quantity="true">
            <field name="date" interval="month" type="row"/>
            <field name="partner_id" type="row"/>
            <field name="category_id" type="col"/>
            <field name="amount" type="measure"/>
            <field name="quantity" type="measure"/>
        </pivot>
    </field>
</record>
```

## Field Widgets

### Common Widgets

| Widget | Description | Field Type |
|--------|-------------|------------|
| `badge` | Colored badge | Selection |
| `boolean_toggle` | Toggle switch | Boolean |
| `char_emojis` | Text with emoji picker | Char |
| `date` | Date picker | Date |
| `daterange` | Date range | Date |
| `float_time` | Hours:minutes | Float |
| `handle` | Drag handle | Integer |
| `html` | HTML editor | Html |
| `image` | Image display | Binary |
| `many2many_tags` | Tag display | Many2many |
| `monetary` | Currency formatted | Float/Monetary |
| `percentage` | Percentage | Float |
| `phone` | Phone link | Char |
| `priority` | Star rating | Selection |
| `progressbar` | Progress bar | Float/Integer |
| `radio` | Radio buttons | Selection |
| `selection_badge` | Badge selection | Selection |
| `statusbar` | Status flow | Selection |
| `url` | Clickable URL | Char |

## Actions

### Window Action

```xml
<record id="my_model_action" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">list,form,kanban,calendar</field>
    <field name="domain">[('active', '=', True)]</field>
    <field name="context">{'default_state': 'draft'}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Create your first record
        </p>
        <p>Click the button to create a new record.</p>
    </field>
</record>
```

### Server Action

```xml
<record id="action_confirm_all" model="ir.actions.server">
    <field name="name">Confirm All</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_view_types">list</field>
    <field name="state">code</field>
    <field name="code">
        records.action_confirm()
    </field>
</record>
```

## Menu Items

```xml
<!-- Root menu -->
<menuitem id="my_module_menu_root"
          name="My Module"
          sequence="10"/>

<!-- Category menu -->
<menuitem id="my_module_menu_category"
          name="Operations"
          parent="my_module_menu_root"
          sequence="10"/>

<!-- Action menu -->
<menuitem id="my_model_menu"
          name="My Models"
          parent="my_module_menu_category"
          action="my_model_action"
          sequence="10"/>
```

## View Inheritance

### Extend View

```xml
<record id="view_partner_form_inherit" model="ir.ui.view">
    <field name="name">res.partner.form.inherit</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <!-- Add field after another -->
        <field name="phone" position="after">
            <field name="custom_field"/>
        </field>

        <!-- Add field before another -->
        <field name="email" position="before">
            <field name="secondary_email"/>
        </field>

        <!-- Replace field -->
        <field name="website" position="replace">
            <field name="website" widget="url" placeholder="https://..."/>
        </field>

        <!-- Add attributes -->
        <field name="name" position="attributes">
            <attribute name="required">True</attribute>
            <attribute name="invisible">context.get('hide_name')</attribute>
        </field>

        <!-- Add inside element -->
        <xpath expr="//page[@name='sales']" position="inside">
            <field name="custom_info"/>
        </xpath>

        <!-- Remove element -->
        <field name="old_field" position="replace"/>
    </field>
</record>
```

### XPath Expressions

```xml
<!-- By field name -->
<xpath expr="//field[@name='partner_id']" position="after"/>

<!-- By page name -->
<xpath expr="//page[@name='details']" position="inside"/>

<!-- By class -->
<xpath expr="//div[hasclass('oe_title')]" position="inside"/>

<!-- By element -->
<xpath expr="//notebook" position="inside"/>
<xpath expr="//sheet" position="before"/>

<!-- Multiple conditions -->
<xpath expr="//field[@name='amount'][@widget='monetary']" position="replace"/>
```

## Conditional Display

Use Python expressions with `invisible` attribute:

```xml
<!-- Hide based on field value -->
<field name="discount" invisible="not has_discount"/>

<!-- Hide based on state -->
<button name="action_confirm" invisible="state != 'draft'"/>

<!-- Complex conditions -->
<field name="special_field" invisible="state not in ['confirmed', 'done'] or not is_admin"/>

<!-- Based on context -->
<field name="internal_field" invisible="context.get('hide_internal')"/>
```

## QWeb Templates (Reports)

```xml
<template id="report_my_model_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2><t t-esc="doc.name"/></h2>
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th class="text-end">Quantity</th>
                                <th class="text-end">Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="doc.line_ids" t-as="line">
                                <tr>
                                    <td><t t-esc="line.product_id.name"/></td>
                                    <td class="text-end"><t t-esc="line.quantity"/></td>
                                    <td class="text-end">
                                        <t t-esc="line.price"
                                           t-options="{'widget': 'monetary', 'display_currency': doc.currency_id}"/>
                                    </td>
                                </tr>
                            </t>
                        </tbody>
                    </table>
                </div>
            </t>
        </t>
    </t>
</template>
```
