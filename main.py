import os
import re
import secrets
from fasthtml.common import *
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from components.layout import app_styles, Page
from pages.home import home_page
from pages.about import about_page
from pages.contact import contact_page
from pages.legal import delete_account_page, privacy_page
from utils.i18n import get_lang, t

from starlette.responses import JSONResponse as _JSONResponse

from db import init_db

def _detect_lang_before(req, sess):
    """On first visit, default the UI language from the visitor's IP country."""
    try:
        from utils.i18n import ensure_detected_lang
        ensure_detected_lang(sess, req)
    except Exception:
        pass


app, rt = fast_app(
    hdrs=(app_styles(),),
    default_hdrs=False,
    pico=False,
    surreal=False,
    htmx=False,
    htmlkw={'lang': 'en'},
    secret_key=os.environ.get('APP_SECRET') or secrets.token_hex(32),
    before=Beforeware(
        _detect_lang_before,
        skip=[r'/health', r'/static/.*', r'/api/.*', r'/set-lang/.*', r'/favicon\.ico'],
    ),
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@rt("/health")
def health():
    return _JSONResponse({"status": "ok"})


# --- Language switching ---

@rt('/set-lang/{code}')
def set_language(code: str, sess):
    from utils.i18n import set_lang, LANGUAGES
    if code in LANGUAGES:
        set_lang(sess, code)
    return RedirectResponse('/', status_code=303)


# --- Public pages ---

@rt
def index(sess):
    return Page(home_page(sess=sess), active='home', sess=sess)

@rt
def about(sess):
    lang = get_lang(sess)
    return Page(about_page(lang), active='about', title=t('nav_about', lang), sess=sess)

@rt
def changelog(sess):
    from pages.changelog import changelog_page
    return Page(changelog_page(), title='Changelog', sess=sess)

@rt
def contact(sess, name: str = '', email: str = '', message: str = '', website: str = '', sent: str = '',
            request=None):
    from utils.contact import check_contact, deliver_contact
    lang = get_lang(sess)
    error = ''
    if request and request.method == 'POST':
        if website:  # honeypot filled in: a bot; pretend it worked and send nothing
            return RedirectResponse('/contact?sent=1', status_code=303)
        problem = check_contact(name, email, message)
        if problem:
            error = t(problem, lang)
        elif deliver_contact(name, email, message, lang=lang):
            return RedirectResponse('/contact?sent=1', status_code=303)
        else:
            error = t('contact_send_failed', lang)
    return Page(
        contact_page(name=name, email=email, message=message, error=error, sent=sent == '1', lang=lang),
        active='contact', title=t('nav_contact', lang), sess=sess,
    )

@rt
def privacy(sess):
    return Page(privacy_page(), title='Privacy policy', sess=sess)

@rt('/delete-account')
def delete_account(sess):
    return Page(delete_account_page(), title='Delete account', sess=sess)


# --- Chat routes ---

from chat.routes import register_chat_routes
register_chat_routes(rt)

# --- Auth routes ---

from auth.routes import register_auth_routes
register_auth_routes(rt)

# --- Admin routes ---

from admin.routes import register_admin_routes
register_admin_routes(rt)


# --- Mount the optional FastAPI layer at /api/v1 ---

_api_status = {"mounted": False, "error": None}
try:
    from api.app import api_router
    app.mount("/api/v1", api_router)
    _api_status["mounted"] = True
    print("INFO:     FastAPI layer mounted at /api/v1 (docs: /api/v1/docs)")
except ImportError as e:
    _api_status["error"] = f"ImportError: {e}"
    print("INFO:     FastAPI not installed — API layer disabled (monolith mode)")
except Exception as e:
    _api_status["error"] = f"{type(e).__name__}: {e}"
    print(f"ERROR:    Failed to mount mobile API: {e}")

@rt("/api-status")
def api_status():
    return _JSONResponse(_api_status)


# --- Initialize DB on startup ---

@app.on_event("startup")
async def startup():
    try:
        init_db()
    except Exception as e:
        print(f"DB init warning: {e}")


from voice import register_voice_routes
register_voice_routes(app)

serve(port=int(os.environ.get('PORT', 5011)), reload=False)
