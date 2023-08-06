from .forms import LoginForm

def login_form(request):
    return {
        'luxuryadmin': {
            'forms': {
                'login': LoginForm
            }
        }
    }
