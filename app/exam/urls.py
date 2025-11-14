from django.urls import path
from . import views

urlpatterns = [
    # Exams
    path('exams/', views.ExamsAPIView.as_view(), name='exams-list-create'),
    path('exams/<int:pk>/', views.ExamDetailAPIView.as_view(), name='exams-detail'),
    path('exams/<int:pk>/statistics/', views.ExamStatisticsAPIView.as_view(), name='exams-statistics'),

    # Submissions
    path('submissions/', views.SubmissionsAPIView.as_view(), name='submissions-list-create'),
    path('submissions/status/', views.SubmissionStatusAPIView.as_view(), name='submissions-status'),
    path('submissions/<int:pk>/', views.SubmissionDetailAPIView.as_view(), name='submissions-detail'),
    path('submissions/student_submission/', views.StudentSubmissionsAPIView.as_view(), name='submissions-student'),
    path('submissions/<int:pk>/detailed_analysis/', views.SubmissionDetailedAnalysisAPIView.as_view(), name='submissions-detailed-analysis'),
    path('submissions/student/<int:student_id>/exam/<int:exam_id>/', views.StudentExamResultsAPIView.as_view(), name='submissions-student-exam'),
    path('results/<int:pk>/', views.SubmissionDetailAPIView.as_view(), name='exam-results'),
]