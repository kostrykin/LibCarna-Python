import libcarna


def _strip_prefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s


def add_role_shortcuts(rs: libcarna.render_stage):
    for key in dir(rs):
        if key.startswith('ROLE_DEFAULT_'):

            # Determine the role name
            shortcut = _strip_prefix(key, 'ROLE_DEFAULT_').lower()

            # Add the shortcut to the render stage
            if not hasattr(rs, shortcut):
                role = getattr(rs, key)
                setattr(rs, shortcut, role)
