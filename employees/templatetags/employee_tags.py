# employees/templatetags/employee_tags.py
from django import template

register = template.Library()

@register.filter
def split(value, separator=','):
    """Split a string by separator and return a list"""
    if not value:
        return []
    return [item.strip() for item in value.split(separator) if item.strip()]

@register.filter
def trim(value):
    """Remove whitespace from both ends of a string"""
    if not value:
        return value
    return value.strip()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary"""
    return dictionary.get(key)

@register.filter
def count_permissions(role):
    """Count the number of permissions enabled for a role"""
    permissions = [
        role.can_manage_properties,
        role.can_manage_landlords,
        role.can_manage_residents,
        role.can_manage_employees,
        role.can_handle_payments,
        role.can_handle_maintenance,
        role.can_handle_support_tickets,
        role.can_manage_housekeeping,
        role.can_manage_leads,
        role.can_view_reports,
        role.can_access_crm,
    ]
    return sum(1 for perm in permissions if perm)


@register.filter
def replace(value, arg):
    """
    Replace occurrences of 'old' with 'new' in a string.
    Usage: {{ value|replace:"old:new" }} or {{ value|replace:"old,new" }}
    """
    if not value:
        return value
    
    # Handle both colon and comma separators
    if ':' in arg:
        old, new = arg.split(':', 1)
    elif ',' in arg:
        old, new = arg.split(',', 1)
    else:
        return value  # Invalid format
    
    return value.replace(old, new)

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter
def div(value, arg):
    """Divide the value by the argument."""
    try:
        if float(arg) == 0:
            return ''
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return ''












