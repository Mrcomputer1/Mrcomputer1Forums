from django import template
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.templatetags.staticfiles import static

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

    # Emoji Shortcuts
    s = s.replace(":=)", ":)")
    s = s.replace("(:", ":)")
    s = s.replace(":smile:", ":)")

    s = s.replace(":p", ":P")
    s = s.replace(":tongue:", ":P")

    s = s.replace(":wink:", ";)")

    s = s.replace("$P", ":money:")
    s = s.replace(":$", ":money:")
    s = s.replace(":moneyeyes", ":money:")

    # Emoji
    # Emoji provided free by http://emojione.com
    
    s = s.replace(":angry:", "<img class='emoji' src='" + static("Mrcomputer1Forums/emoji/angry.png") + "' alt='Angry (:angry:)'>")
    s = s.replace(":)", "<img class='emoji' src='" + static("Mrcomputer1Forums/emoji/smile.png") + "' alt='Smile (:))'>")
    s = s.replace(":P", "<img class='emoji' src='" + static("Mrcomputer1Forums/emoji/tongue.png") + "' alt='Tongue (:P)'>")
    s = s.replace(";)", "<img class='emoji' src='" + static("Mrcomputer1Forums/emoji/wink.png") + "' alt='Wink (;))'>")
    s = s.replace(":sick:", "<img class='emoji' src='" + static("Mrcomputer1Forums/emoji/sick.png") + "' alt='Sick (:sick:)'>")
    s = s.replace(":cool:", "<img class='emoji' src='" + static("Mrcomputer1Forums/emoji/cool.png") + "' alt='Cool (:cool:)'>")
    s = s.replace(":money:", "<img class='emoji' src='" + static("Mrcomputer1Forums/emoji/money.png") + "' alt='Money Eyes and Tongue (:money:)'>")
    s = s.replace(":+1:", "<img class='emoji' src='" + static("Mrcomputer1Forums/emoji/thumbs-up.png") + "' alt='Thumbs Up (:+1:)'>")
    s = s.replace(":-1:", "<img class='emoji' src='" + static("Mrcomputer1Forums/emoji/thumbs-down.png") + "' alt='Thumbs Down (:-1:)'>")
    
    return mark_safe(s)
