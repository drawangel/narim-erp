# Odoo 18 Controllers Reference

## Controller Basics

Controllers handle HTTP requests in Odoo. They're defined in the `controllers/` directory.

### Basic Controller Structure

```python
# controllers/__init__.py
from . import main

# controllers/main.py
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    @http.route('/my/page', type='http', auth='user', website=True)
    def my_page(self, **kwargs):
        return request.render('my_module.my_template', {
            'records': request.env['my.model'].search([]),
        })
```

## Route Decorator Parameters

```python
@http.route(
    route='/my/path/<int:id>',  # URL pattern
    type='http',                 # 'http' or 'json'
    auth='user',                 # 'user', 'public', 'none'
    methods=['GET', 'POST'],     # Allowed methods
    website=True,                # Website context
    sitemap=True,                # Include in sitemap
    csrf=True,                   # CSRF protection (default True)
    cors='*',                    # CORS header
    save_session=True,           # Save session after request
)
def my_endpoint(self, id, **kwargs):
    pass
```

### Authentication Types

| Auth | Description |
|------|-------------|
| `user` | Logged in users only |
| `public` | Anyone (creates public user session) |
| `none` | No authentication, no environment |

### Route Patterns

```python
# Basic path
@http.route('/my/page')

# With parameters
@http.route('/my/record/<int:record_id>')
@http.route('/my/record/<model("my.model"):record>')  # Direct record

# Multiple routes
@http.route(['/my/page', '/my/alternate-page'])

# Regex patterns
@http.route('/my/<string:slug>')
```

## HTTP Controllers

### Rendering Templates

```python
@http.route('/my/dashboard', type='http', auth='user', website=True)
def dashboard(self):
    records = request.env['my.model'].search([], limit=10)
    return request.render('my_module.dashboard_template', {
        'records': records,
        'user': request.env.user,
    })
```

### Redirects

```python
@http.route('/my/action', type='http', auth='user')
def do_action(self, **kwargs):
    # Process action
    return request.redirect('/my/success')

# With external URL
return request.redirect('https://example.com', local=False)
```

### File Downloads

```python
@http.route('/my/download/<int:record_id>', type='http', auth='user')
def download_file(self, record_id):
    record = request.env['my.model'].browse(record_id)
    record.check_access_rights('read')

    return request.make_response(
        record.file_content,
        headers=[
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', f'attachment; filename="{record.filename}"'),
        ]
    )
```

### File Uploads

```python
@http.route('/my/upload', type='http', auth='user', methods=['POST'], csrf=True)
def upload_file(self, file, **kwargs):
    if file:
        data = base64.b64encode(file.read())
        record = request.env['my.model'].create({
            'name': file.filename,
            'file_data': data,
        })
        return request.redirect(f'/my/record/{record.id}')
    return request.redirect('/my/upload-error')
```

## JSON Controllers

### JSON-RPC Endpoint

```python
@http.route('/my/api/data', type='json', auth='user')
def get_data(self, domain=None, limit=10):
    """
    Called via JSON-RPC:
    POST /my/api/data
    Content-Type: application/json
    {"jsonrpc": "2.0", "method": "call", "params": {"domain": [], "limit": 5}}
    """
    records = request.env['my.model'].search(domain or [], limit=limit)
    return records.read(['name', 'value'])
```

### Public JSON API

```python
@http.route('/api/v1/products', type='json', auth='public', cors='*')
def api_products(self, **kwargs):
    products = request.env['product.product'].sudo().search([
        ('sale_ok', '=', True),
    ], limit=kwargs.get('limit', 50))

    return [{
        'id': p.id,
        'name': p.name,
        'price': p.list_price,
    } for p in products]
```

## Request Object

```python
from odoo.http import request

# Environment
request.env                # Current environment
request.env.user          # Current user
request.env.company       # Current company
request.env.context       # Context dict
request.env.cr            # Database cursor
request.env.uid           # Current user ID

# HTTP Data
request.httprequest       # Werkzeug request
request.params            # GET/POST parameters
request.session           # Session data

# Website (if website=True)
request.website           # Current website
request.lang              # Current language

# Render
request.render('template', values)
request.redirect('/path')
request.make_response(data, headers)
```

## Portal Controllers

### Extending Portal

```python
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request

class MyPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'my_count' in counters:
            values['my_count'] = request.env['my.model'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
            ])
        return values

    @http.route('/my/records', type='http', auth='user', website=True)
    def my_records(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        domain = [('partner_id', '=', partner.id)]

        records = request.env['my.model'].search(domain)

        return request.render('my_module.portal_my_records', {
            'records': records,
            'page_name': 'my_records',
        })

    @http.route('/my/record/<int:record_id>', type='http', auth='user', website=True)
    def my_record_detail(self, record_id, **kwargs):
        record = request.env['my.model'].browse(record_id)

        # Security check
        if record.partner_id != request.env.user.partner_id:
            return request.redirect('/my')

        return request.render('my_module.portal_record_detail', {
            'record': record,
            'page_name': 'my_records',
        })
```

## Error Handling

```python
from odoo.exceptions import AccessError, UserError, ValidationError
from werkzeug.exceptions import NotFound, Forbidden

@http.route('/my/record/<int:record_id>', type='http', auth='user')
def record_detail(self, record_id):
    try:
        record = request.env['my.model'].browse(record_id)
        record.check_access_rights('read')
        record.check_access_rule('read')
    except AccessError:
        raise Forbidden("You don't have access to this record")

    if not record.exists():
        raise NotFound("Record not found")

    return request.render('my_module.template', {'record': record})
```

### JSON Error Response

```python
@http.route('/api/record/<int:record_id>', type='json', auth='user')
def api_record(self, record_id):
    record = request.env['my.model'].browse(record_id)

    if not record.exists():
        return {'error': 'not_found', 'message': 'Record not found'}

    try:
        record.check_access_rights('read')
    except AccessError:
        return {'error': 'access_denied', 'message': 'Access denied'}

    return {'success': True, 'data': record.read()[0]}
```

## Session and Cookies

```python
@http.route('/my/preferences', type='http', auth='user')
def preferences(self, **kwargs):
    # Read from session
    theme = request.session.get('theme', 'light')

    # Write to session
    if 'theme' in kwargs:
        request.session['theme'] = kwargs['theme']

    return request.render('my_module.preferences', {'theme': theme})

@http.route('/my/set-cookie', type='http', auth='public')
def set_cookie(self):
    response = request.redirect('/my/page')
    response.set_cookie('my_cookie', 'value', max_age=3600)
    return response
```

## CSRF Protection

CSRF is enabled by default. For forms:

```xml
<form method="POST" action="/my/submit">
    <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
    <!-- form fields -->
</form>
```

To disable for specific route (not recommended):

```python
@http.route('/api/webhook', type='json', auth='none', csrf=False)
def webhook(self, **kwargs):
    # Validate request another way
    pass
```

## Website Snippets

### Snippet Controller

```python
@http.route('/my_module/snippet/data', type='json', auth='public', website=True)
def snippet_data(self, **kwargs):
    """Provide data for dynamic snippet."""
    return {
        'items': request.env['my.model'].sudo().search_read(
            [], ['name', 'image'], limit=6
        ),
    }
```

## REST API Pattern

```python
class MyAPI(http.Controller):

    @http.route('/api/v1/records', type='json', auth='user', methods=['GET'])
    def list_records(self, offset=0, limit=20, **kwargs):
        records = request.env['my.model'].search([], offset=offset, limit=limit)
        return {
            'count': request.env['my.model'].search_count([]),
            'records': records.read(['name', 'value']),
        }

    @http.route('/api/v1/records/<int:id>', type='json', auth='user', methods=['GET'])
    def get_record(self, id):
        record = request.env['my.model'].browse(id)
        if not record.exists():
            return {'error': 'not_found'}
        return record.read()[0]

    @http.route('/api/v1/records', type='json', auth='user', methods=['POST'])
    def create_record(self, **kwargs):
        record = request.env['my.model'].create(kwargs)
        return {'id': record.id}

    @http.route('/api/v1/records/<int:id>', type='json', auth='user', methods=['PUT'])
    def update_record(self, id, **kwargs):
        record = request.env['my.model'].browse(id)
        if not record.exists():
            return {'error': 'not_found'}
        record.write(kwargs)
        return {'success': True}

    @http.route('/api/v1/records/<int:id>', type='json', auth='user', methods=['DELETE'])
    def delete_record(self, id):
        record = request.env['my.model'].browse(id)
        if not record.exists():
            return {'error': 'not_found'}
        record.unlink()
        return {'success': True}
```
