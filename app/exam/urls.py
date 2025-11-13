from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configuração do router para ViewSets
router = DefaultRouter()
router.register(r'exams', views.ExamViewSet)
router.register(r'submissions', views.ExamSubmissionViewSet)

urlpatterns = [
    # URLs dos ViewSets
    path('', include(router.urls)),
    
    # URLs personalizadas (mantidas para compatibilidade)
    path('submit/', views.ExamSubmissionViewSet.as_view({'post': 'create'}), name='submit_exam'),
    path('results/<int:pk>/', views.ExamSubmissionViewSet.as_view({'get': 'retrieve'}), name='exam_results'),
]