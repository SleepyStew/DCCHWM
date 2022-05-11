import re
from jinja2 import pass_eval_context
from markupsafe import Markup, escape

@pass_eval_context
def newline_to_br(eval_ctx, value):
    value = escape(value)
    br = Markup(br)
    result = "\n\n".join(
        f"<p>{br.join(p.splitlines())}<\p>"
        for p in re.split(r"(?:\r\n|\r(?!\n)|\n){2,}", value)
    )
    return Markup(result) if autoescape else result
