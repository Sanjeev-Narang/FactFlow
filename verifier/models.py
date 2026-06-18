from django.db import models

class UploadedDocument(models.Model):
    """
    Tracks the uploaded PDF metadata and the overall progress of its verification.
    No physical FileField is used to support clean, stateless cloud deployments.
    """
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.file_name} ({self.status})"


class FactCheckClaim(models.Model):
    """
    Stores each individual statement isolated from the PDF and its verified result.
    Linked to its parent UploadedDocument.
    """
    VERDICT_CHOICES = [
        ('Verified', 'Verified'),
        ('Inaccurate', 'Inaccurate'),
        ('False', 'False'),
    ]

    # The related_name='claims' enables DocumentReportSerializer to pull this reverse relation
    document = models.ForeignKey(
        UploadedDocument, 
        on_delete=models.CASCADE, 
        related_name='claims'
    )
    
    extracted_claim = models.TextField(
        help_text="The raw statistic or statement pulled from the PDF text."
    )
    
    # Verification details mapped to your assignment requirements
    verdict = models.CharField(
        max_length=20, 
        choices=VERDICT_CHOICES, 
        blank=True, 
        null=True
    )
    confidence_score = models.FloatField(blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    corrected_fact = models.TextField(
        blank=True, 
        null=True, 
        help_text="The actual factual info retrieved from the Tavily search layer."
    )
    
    verified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Claim {self.id} [{self.verdict}]: {self.extracted_claim[:30]}..."
