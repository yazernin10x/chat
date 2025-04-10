from django import template

register = template.Library()


@register.filter(name="alert_class")
def alert_class(level_tag: str) -> str:
    alert_classes = {
        "success": "alert-success",
        "error": "alert-error",
        "warning": "alert-warning",
        "info": "alert-info",
    }
    return alert_classes.get(level_tag, "alert-info")
