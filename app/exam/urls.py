from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_exam, name='submit_exam'),
    path('results/<int:submission_id>/', views.exam_results, name='exam_results'),
    path('student/<int:student_id>/exam/<int:exam_id>/results/', 
         views.student_exam_results, name='student_exam_results'),
]