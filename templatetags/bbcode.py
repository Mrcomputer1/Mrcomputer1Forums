from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='parse', is_safe=True, needs_autoescape=False)
def parse(value):
    s = value

    # HTML
    s = s.replace("<", "&gt;")
    s = s.replace(">", "&lt;")
    s = s.replace("&", "&amp;")

    # Shortcuts
    s = s.replace("[s]", "[del]")
    s = s.replace("[/s]", "[/del]")
    
    # Simple
    s = s.replace("[img]", "<img src='")
    s = s.replace("[b]", "<b>")
    s = s.replace("[i]", "<i>")
    s = s.replace("[u]", "<u>")
    s = s.replace("[del]", "<del>")
    s = s.replace("[quote]", "<div class='post-quote'>")
    s = s.replace("[center]", "<center>")
    s = s.replace("[small]", "<small>")
    s = s.replace("[big]", "</big>")
    
    # Useful Stuff
    s = s.replace("\n", "<br>")

    # Links
    s = s.replace("[url]", "<a ")
    s = s.replace("(link)", "href='")
    s = s.replace("(/link)", "'>")
    s = s.replace("[/url]", "</a>")
    
    # Endings
    s = s.replace("[/img]", "'></img>")
    s = s.replace("[/b]", "</b>")
    s = s.replace("[/i]", "</i>")
    s = s.replace("[/u]", "</u>")
    s = s.replace("[/del]", "</del>")
    s = s.replace("[/quote]", "</div>")
    s = s.replace("[/center]", "</center>")
    s = s.replace("[/small]", "</small>")
    s = s.replace("[/big]", "</big>")
    

    return mark_safe(s)
