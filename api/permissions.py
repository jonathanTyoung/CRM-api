def is_crm_admin(user) -> bool:
    """
    Returns True for Django superusers and agents with role='admin'.
    Use this instead of checking is_staff/is_superuser OR agent_profile.role
    inconsistently across views.
    """
    return user.is_superuser or (
        hasattr(user, "agent_profile") and user.agent_profile.role == "admin"
    )
