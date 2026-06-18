import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DropZone from './components/DropZone';
import ReportViewer from './components/ReportViewer';
import { ShieldCheck, Cpu, HardDriveDownload } from 'lucide-react';
import styles from './App.module.css';

const API_BASE_URL = '/api';

export default function App() {
  const [currentJob, setCurrentJob] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    let intervalId;

    if (currentJob && currentJob.status === 'processing') {
      intervalId = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/results/${currentJob.id}/`);
          
          if (!response.ok) {
            throw new Error("Job tracking lookup failed.");
          }

          const contentType = response.headers.get('content-type');

          // Check if response has transitioned from JSON status to the physical binary PDF File
          if (contentType && contentType.includes('application/pdf')) {
            clearInterval(intervalId);
            
            // Convert byte array chunk stream to clear browser link payload
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            
            const anchor = document.createElement('a');
            anchor.href = downloadUrl;
            anchor.download = `verified_report_${currentJob.file_name}`;
            document.body.appendChild(anchor);
            anchor.click();
            
            // Clean up memory allocations
            document.body.removeChild(anchor);
            window.URL.revokeObjectURL(downloadUrl);

            setCurrentJob(prev => ({ ...prev, status: 'completed' }));
            setIsProcessing(false);
          } else {
            // Still in 'processing' status, update with JSON payload data
            const data = await response.json();
            if (data.status === 'failed') {
              setCurrentJob(data);
              setIsProcessing(false);
              clearInterval(intervalId);
            }
          }
        } catch (err) {
          console.error("Polling error:", err);
          setCurrentJob(prev => ({
            ...prev,
            status: 'failed',
            error_message: 'Connection dropped while waiting for file response asset.'
          }));
          setIsProcessing(false);
          clearInterval(intervalId);
        }
      }, 2500); // Polls every 2.5 seconds
    }

    return () => clearInterval(intervalId);
  }, [currentJob]);

  const handleFileSubmission = async (file) => {
    setIsProcessing(true);
    setCurrentJob({ file_name: file.name, status: 'processing' });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/upload/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        // Sets tracking row context state including primary database key ID
        setCurrentJob(data); 
      } else {
        const errorData = await response.json();
        setCurrentJob({
          file_name: file.name,
          status: 'failed',
          error_message: errorData.error || 'Server rejected file upload multipart format.'
        });
        setIsProcessing(false);
      }
    } catch (error) {
      setCurrentJob({
        file_name: file.name,
        status: 'failed',
        error_message: 'Unable to communicate with endpoint upload gateway.'
      });
      setIsProcessing(false);
    }
  };

  return (
    <div className={styles.appLayout}>
      <Header />
      
      <main className={styles.mainContent}>
        <div className={styles.heroSection}>
          <h1 className={styles.mainTitle}>PDF Fact-Check Analysis</h1>
          <p className={styles.mainSubtitle}>
            Verify statistical assertions instantly. Drop your document to parse 
            claims and trigger live search cross-referencing.
          </p>
        </div>

        <DropZone onFileSelected={handleFileSubmission} isProcessing={isProcessing} />
        
        <ReportViewer data={currentJob} />

        {!currentJob && (
          <div className={styles.featuresGrid}>
            <div className={styles.featureCard}>
              <ShieldCheck className={styles.featureIcon} />
              <div>
                <h4 className={styles.featureTitle}>Automated Search Verification</h4>
                <p className={styles.featureDescription}>Claims run concurrently through Tavily API search engines.</p>
              </div>
            </div>
            <div className={styles.featureCard}>
              <Cpu className={styles.featureIcon} />
              <div>
                <h4 className={styles.featureTitle}>Stateless Architecture</h4>
                <p className={styles.featureDescription}>Binary assets remain strictly in RAM to protect enterprise privacy.</p>
              </div>
            </div>
            <div className={styles.featureCard}>
              <HardDriveDownload className={styles.featureIcon} />
              <div>
                <h4 className={styles.featureTitle}>Direct PDF Delivery</h4>
                <p className={styles.featureDescription}>Receive a clean, highlighted evaluation summary PDF automatically.</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
