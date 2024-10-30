# EVENT_LISTEN_TYPES
EVENT_LISTEN_BEFORE_INSERT = 'before_insert'
EVENT_LISTEN_AFTER_INSERT = 'after_insert'
EVENT_LISTEN_BEFORE_UPDATE = 'before_update'
EVENT_LISTEN_AFTER_UPDATE = 'after_update'
EVENT_LISTEN_BEFORE_DELETE = 'before_delete'
EVENT_LISTEN_AFTER_DELETE = 'after_delete'

# Audit logs type of actions
AUDIT_LOGS_ACTIONS = {
    EVENT_LISTEN_AFTER_INSERT: 'INSERT',
    EVENT_LISTEN_BEFORE_UPDATE: 'UPDATE',
    EVENT_LISTEN_BEFORE_DELETE: 'DELETE'
}