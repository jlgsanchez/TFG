"""Django_Xterm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('Django_Xterm_Pyserial.urls')),
    path('admin/', admin.site.urls),
]

handler400 = "Django_Xterm_Pyserial.views.my_bad_request_found_view"
handler401 = "Django_Xterm_Pyserial.views.my_not_authorized_view"
handler403 = "Django_Xterm_Pyserial.views.my_forbidden_view"
handler404 = "Django_Xterm_Pyserial.views.my_page_not_found_view"
handler500 = "Django_Xterm_Pyserial.views.my_page_server_error_view"
handler503 = "Django_Xterm_Pyserial.views.my_service_unavailable_view"
