# -*- coding:utf-8 -*-
"""
@author:TANYIPENG631
@file: urls.py
@time: 2018/12/6  16:53
"""
from django.urls import path

from . import views

app_name = 'hr_search_engine'
urlpatterns = [
    path('naive/', views.naive, name='naive'),
    path('categories/', views.categories, name='categories'),
    path('custom/', views.custom, name='custom'),
    path('query_recommend/', views.query_recommend, name='query_recommend'),
    path('es/esquery', views.esquery, name='esquery'),
]