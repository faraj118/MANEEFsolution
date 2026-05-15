from frappe import _

def get_data():
    return {
        'fieldname': 'custom_project_charter',
        'non_standard_fieldnames': {
            'Project': 'project_charter',
            'Risk Assessment': 'project_charter',
        },
        'transactions': [
            {
                'label': _('Sales'),
                'items': ['Sales Order']
            },
            {
                'label': _('Operations'),
                'items': ['Project']
            },
            {
                'label': _('Risk & Assessment'),
                'items': ['Risk Assessment']
            }
        ]
    }
