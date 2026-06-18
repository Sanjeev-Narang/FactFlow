import threading
from django.http import FileResponse
from rest_framework import request, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UploadedDocument
from .serializers import DocumentReportSerializer, PDFUploadSerializer
from .services.pipeline import FactCheckPipeline
from .services.pdf_gen import DocumentPDFExportService  # 🚀 IMPORT NEW EXPORT ENGINE


# ── Background worker ─────────────────────────────────────────────────────────

def run_pipeline_in_background(doc_id: int, file_bytes: bytes) -> None:
    doc_record = None
    try:
        doc_record = UploadedDocument.objects.get(id=doc_id)
        pipeline = FactCheckPipeline()
        pipeline.process_document(doc_record, file_bytes)

        doc_record.status = "completed"
        doc_record.save(update_fields=["status"])

    except UploadedDocument.DoesNotExist:
        pass
    except Exception as exc:
        if doc_record is not None:
            doc_record.status = "failed"
            doc_record.error_message = str(exc)
            doc_record.save(update_fields=["status", "error_message"])


# ── Upload endpoint ───────────────────────────────────────────────────────────

class FactCheckUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = PDFUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data["file"]

        doc_record = UploadedDocument.objects.create(
            file_name=uploaded_file.name,
            status="processing",
        )

        file_bytes = uploaded_file.read()

        thread = threading.Thread(
            target=run_pipeline_in_background,
            args=(doc_record.id, file_bytes),
            daemon=True,
        )
        thread.start()

        return Response(
            DocumentReportSerializer(doc_record).data,
            status=status.HTTP_202_ACCEPTED,
        )


# ── Polling & PDF Downloader Endpoint ──────────────────────────────────────────

class FactCheckResultView(APIView):
    """
    GET /api/results/<doc_id>/
    - Returns JSON status when processing or failed so UI can display state updates.
    - Swaps response to a streaming file attachment download output once complete.
    """

    def get(self, request, doc_id: int, *args, **kwargs):
        try:
            # Optimize lookups using prefetched claims instances
            doc_record = UploadedDocument.objects.prefetch_related("claims").get(id=doc_id)
        except UploadedDocument.DoesNotExist:
            return Response(
                {"detail": "Document reference not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 1. If still processing or failed, send back standard tracking status objects
        if doc_record.status != "completed":
            return Response(
                DocumentReportSerializer(doc_record).data,
                status=status.HTTP_200_OK,
            )

        # 2. 🚀 OPTIMIZATION: If processing finished, swap to physical file download delivery stream
        try:
            pdf_service = DocumentPDFExportService()
            pdf_buffer = pdf_service.generate_report_pdf(doc_record)
            
            # Format the download file name cleanly (e.g., verified_exp_doc.pdf)
            export_filename = f"verified_{doc_record.file_name.replace(' ', '_')}"
            if not export_filename.lower().endswith('.pdf'):
                export_filename += '.pdf'

            return FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=export_filename,
                content_type='application/pdf'
            )
            
        except Exception as export_error:
            return Response(
                {"detail": f"Failed to assemble printable report document asset: {str(export_error)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
