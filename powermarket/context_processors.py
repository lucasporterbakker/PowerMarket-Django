from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


def nice_greeting(request):
    current_time = timezone.now()
    decimal_hour = current_time.hour + current_time.minute / 60

    if decimal_hour:
        # From 4:30 to 12:30.
        if 4.5 <= decimal_hour < 12.5:
            greeting = _("Good morning")
        # From 12:30 to 17:00.
        elif 12.5 <= decimal_hour < 17:
            greeting = _("Good afternoon")
        # Later than 17:00.
        else:
            greeting = _("Good evening")

    else:
        greeting = _("Dear")

    return {
        "nice_greeting": greeting,
    }
