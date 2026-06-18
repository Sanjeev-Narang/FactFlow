from rest_framework import serializers
from .models import UploadedDocument, FactCheckClaim

class PDFUploadSerializer(serializers.Serializer):
    """Validates the incoming multi-part form data request."""
    file = serializers.FileField(write_only=True)

    def validate_file(self, value):
        """Ensure the uploaded file is strictly a PDF and within limits."""
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF documents are supported.")
        
        # Limit file size to 10MB to protect memory allocation during parsing
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        return value


class FactCheckClaimSerializer(serializers.ModelSerializer):
    """Serializes individual claims with their respective verification verdicts."""
    class Meta:
        model = FactCheckClaim
        fields = [
            'id', 
            'extracted_claim', 
            'verdict', 
            'confidence_score', 
            'explanation', 
            'corrected_fact', 
            'verified_at'
        ]
        read_only_fields = fields


class DocumentReportSerializer(serializers.ModelSerializer):
    """
    The final structured payload containing the document parsing status,
    metadata, and its full nested list of verified claims.
    """
    # Maps to the related_name='claims' on the FactCheckClaim foreign key
    claims = FactCheckClaimSerializer(many=True, read_only=True)

    class Meta:
        model = UploadedDocument
        fields = [
            'id', 
            'file_name', 
            'status', 
            'uploaded_at', 
            'error_message', 
            'claims'
        ]
        read_only_fields = fields
