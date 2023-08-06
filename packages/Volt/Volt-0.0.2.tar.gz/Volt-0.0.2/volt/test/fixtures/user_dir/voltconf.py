from volt.config import Config

VOLT = Config(
    TEMPLATE_DIR = "mytemplates",
)

SITE = Config(
    CUSTOM_OPT = "custom_opt_user",
    TITLE = "Title in user",
)

ENGINE_TEST = Config(
    FOO = 'engine foo in user',
    BAR = 'engine bar in user',
)       

ENGINE_TEST_BAD = 'not a Config'

def user_foo(): return "foo in user"

JINJA2_FILTERS = Config(
    foo = user_foo,
)
