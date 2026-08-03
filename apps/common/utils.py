from .models import ActivityLog


def log_activity(actor, action, target=None, **metadata):
    ActivityLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        target_type=target.__class__.__name__ if target else "",
        target_id=str(getattr(target, "pk", "")),
        metadata=metadata,
    )
