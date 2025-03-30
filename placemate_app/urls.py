from django.urls import path

from .view.login import login
from .view.dashboard import dashboard
# from .view.logout import logout

urlpatterns = [
    path('', dashboard, name="dashboard"),
    path('login/', login, name="login"),
    # path('logout/', logout, name="logout"),
]