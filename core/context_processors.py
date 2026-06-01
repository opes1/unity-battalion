from .models import BattalionInfo, ContactInfo


def contact_info(request):
    """
    Injects ContactInfo and BattalionInfo singletons into every template
    context so base.html (footer, navbar) can render dynamic content
    without requiring every view to pass these objects explicitly.
    """
    return {
        'contact_info':  ContactInfo.get_solo(),
        'battalion_info': BattalionInfo.get_solo(),
    }
