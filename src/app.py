"""Flask web application for warehouse management."""
from flask import Flask, render_template, request, redirect, url_for, flash
from warehouse import Warehouse

app = Flask(__name__)
app.secret_key = 'warehouse-app-secret-key'

# In-memory storage for warehouses
warehouses = {}
next_warehouse_id = 1


def get_warehouse_or_redirect(warehouse_id):
    """Return warehouse if exists, else flash error and return None."""
    if warehouse_id in warehouses:
        return warehouses[warehouse_id]
    flash('Warehouse not found', 'error')
    return None


def parse_float(value, default=0):
    """Parse float from string, return default on error."""
    try:
        return float(value) if value else default
    except ValueError:
        return None


def validate_warehouse_form(name, capacity, min_capacity=0):
    """Validate warehouse form data. Returns error message or None."""
    if not name:
        return 'Warehouse name is required'
    if capacity is None:
        return 'Capacity must be a number'
    if capacity <= 0:
        return 'Capacity must be positive'
    if capacity < min_capacity:
        return 'Cannot reduce capacity below current stock'
    return None


@app.route('/')
def index():
    """Overview page showing all warehouses."""
    return render_template('index.html', warehouses=warehouses)


@app.route('/warehouse/<int:warehouse_id>')
def warehouse_detail(warehouse_id):
    """Individual warehouse page showing items."""
    warehouse = get_warehouse_or_redirect(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))
    return render_template(
        'warehouse.html', warehouse=warehouse, warehouse_id=warehouse_id
    )


@app.route('/warehouse/new', methods=['GET', 'POST'])
def create_warehouse():
    """Create a new warehouse."""
    global next_warehouse_id  # pylint: disable=global-statement
    if request.method != 'POST':
        return render_template('create_warehouse.html')

    name = request.form.get('name', '').strip()
    capacity = parse_float(request.form.get('capacity', 0))
    error = validate_warehouse_form(name, capacity)
    if error:
        flash(error, 'error')
        return render_template('create_warehouse.html')

    warehouses[next_warehouse_id] = Warehouse(name, capacity)
    next_warehouse_id += 1
    flash(f'Warehouse "{name}" created successfully', 'success')
    return redirect(url_for('index'))


@app.route('/warehouse/<int:warehouse_id>/edit', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    """Edit warehouse name and capacity."""
    warehouse = get_warehouse_or_redirect(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))

    ctx = {'warehouse': warehouse, 'warehouse_id': warehouse_id}
    if request.method != 'POST':
        return render_template('edit_warehouse.html', **ctx)

    name = request.form.get('name', '').strip()
    capacity = parse_float(request.form.get('capacity', 0))
    error = validate_warehouse_form(name, capacity, warehouse.saldo)
    if error:
        flash(error, 'error')
        return render_template('edit_warehouse.html', **ctx)

    warehouse.name = name
    warehouse.tilavuus = capacity
    flash(f'Warehouse "{name}" updated successfully', 'success')
    return redirect(url_for('warehouse_detail', warehouse_id=warehouse_id))


@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    """Add an item to a warehouse."""
    ctx = {'warehouses': warehouses}
    if request.method != 'POST':
        return render_template('add_item.html', **ctx)

    try:
        warehouse_id = int(request.form.get('warehouse_id', 0))
    except ValueError:
        warehouse_id = None
    if warehouse_id is None or warehouse_id not in warehouses:
        flash('Warehouse not found', 'error')
        return render_template('add_item.html', **ctx)

    item_name = request.form.get('item_name', '').strip()
    quantity = parse_float(request.form.get('quantity', 0))

    if not item_name:
        flash('Item name is required', 'error')
        return render_template('add_item.html', **ctx)
    if quantity is None:
        flash('Quantity must be a number', 'error')
        return render_template('add_item.html', **ctx)

    warehouse = warehouses[warehouse_id]
    success, error = warehouse.add_item(item_name, quantity)
    if not success:
        flash(error, 'error')
        return render_template('add_item.html', **ctx)

    flash(f'Added {quantity} of "{item_name}" to {warehouse.name}', 'success')
    return redirect(url_for('warehouse_detail', warehouse_id=warehouse_id))


@app.route(
    '/warehouse/<int:warehouse_id>/remove-item/<item_name>',
    methods=['POST']
)
def remove_item(warehouse_id, item_name):
    """Remove an item from a warehouse."""
    warehouse = get_warehouse_or_redirect(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))

    quantity_str = request.form.get('quantity', '').strip()
    quantity = parse_float(quantity_str) if quantity_str else None
    if quantity_str and quantity is None:
        flash('Quantity must be a number', 'error')
        return redirect(url_for('warehouse_detail', warehouse_id=warehouse_id))

    success, error = warehouse.remove_item(item_name, quantity)
    if success:
        flash(f'Removed "{item_name}" from {warehouse.name}', 'success')
    else:
        flash(error, 'error')
    return redirect(url_for('warehouse_detail', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/delete', methods=['POST'])
def delete_warehouse(warehouse_id):
    """Delete a warehouse."""
    warehouse = get_warehouse_or_redirect(warehouse_id)
    if not warehouse:
        return redirect(url_for('index'))

    name = warehouse.name
    del warehouses[warehouse_id]
    flash(f'Warehouse "{name}" deleted successfully', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
