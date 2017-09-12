# Server Specific Configurations
server = {
    'port': '8080',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'orm.services.region_manager.rms.controllers.root.RootController',
    'modules': ['orm.services.region_manager.rms'],
    'static_root': '%(confdir)s/../../public',
    'template_path': '%(confdir)s/../templates',
    'debug': True,
    'errors': {
        '404': '/error/404',
        '__force_dict__': True
    }
}

endpoints = {
    'lcp': 'http://127.0.0.1:8082/lcp'
}

# user input validations
region_options = {
    'allowed_status_values': [
        'functional',
        'maintenance',
        'down'
    ],
    'endpoints_types_must_have': [
        'dashboard',
        'identity',
        'ord'
    ]
}

authentication = {
    "enabled": True,
    "mech_id": "admin",
    "mech_pass": "stack",
    "tenant_name": "admin",
    # The Keystone version currently in use. Can be either "2.0" or "3"
    "keystone_version": "2.0",
    "policy_file": "/opt/app/orm/rms/rms/etc/policy.json"
}
