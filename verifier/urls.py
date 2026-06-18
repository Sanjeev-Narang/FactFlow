from django.urls import path
from .views import FactCheckUploadView, FactCheckResultView

urlpatterns = [
    # POST /api/upload/
    path("upload/", FactCheckUploadView.as_view(), name="fact-check-upload"),
    
    # GET /api/results/<doc_id>/
    path("results/<int:doc_id>/", FactCheckResultView.as_view(), name="fact-check-result"),
]
