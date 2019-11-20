from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import *
from apiapp import views

urlpatterns = [

path('book_list/', views.BookListView.as_view()),

]
