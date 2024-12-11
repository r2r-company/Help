from django.urls import path
from . import views
from .views import report_page

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('task/new/', views.task_form, name='task_form'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('task/<int:pk>/edit/', views.task_form, name='task_form'),
    path('task/<int:pk>/change_status/', views.change_task_status, name='change_task_status'),
    path('task/<int:task_id>/update_status/', views.update_performer_status, name='update_performer_status'),
    path('task/<int:pk>/add_message/', views.task_add_message, name='task_add_message'),
    path('task/new/', views.task_create, name='task_create'),
    path('instructions/', views.instructions, name='instructions'),
    path('reports/', report_page, name='reports'),

    path('tasks/<int:task_id>/change_deadline/', views.change_deadline, name='change_deadline'),
    path('tasks/<int:task_id>/add_performer/', views.add_performers, name='add_performer'),

]
