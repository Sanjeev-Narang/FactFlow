import React from 'react';
import { RefreshCw, CheckCircle, AlertOctagon } from 'lucide-react';
import styles from './ReportViewer.module.css';

export default function ReportViewer({ data }) {
  if (!data) return null;

  return (
    <div className={styles.reportCard}>
      <div className={styles.reportHeader}>
        <div className={styles.metaBlock}>
          <span className={styles.label}>Target Document</span>
          <h2 className={styles.fileName}>{data.file_name}</h2>
        </div>
        <div className={styles.statusBlock}>
          <span className={styles.label}>Process Status</span>
          <span className={`${styles.statusBadge} 
            ${data.status === 'processing' ? styles.statusProcessing : ''}
            ${data.status === 'completed' ? styles.statusCompleted : ''}
            ${data.status === 'failed' ? styles.statusFailed : ''}`}
          >
            {data.status === 'processing' && <RefreshCw size={12} className={styles.spin} />}
            {data.status.toUpperCase()}
          </span>
        </div>
      </div>

      <div className={styles.contentSection}>
        {data.status === 'processing' && (
          <div className={styles.statusBox}>
            <RefreshCw size={32} className={`${styles.spin} ${styles.blueIcon}`} />
            <h3 className={styles.statusTitle}>Analyzing Document Assertions...</h3>
            <p className={styles.statusText}>
              Gemini is isolating factual metrics and launching parallel search lookups. Please hold.
            </p>
          </div>
        )}

        {data.status === 'completed' && (
          <div className={styles.statusBox}>
            <CheckCircle size={32} className={styles.greenIcon} />
            <h3 className={styles.statusTitle}>Verification Complete!</h3>
            <p className={styles.statusText}>
              Your fact-check report has been compiled into a highlighted PDF and downloaded.
            </p>
          </div>
        )}

        {data.status === 'failed' && (
          <div className={styles.statusBox}>
            <AlertOctagon size={32} className={styles.redIcon} />
            <h3 className={styles.statusTitle}>Processing Failed</h3>
            <p className={styles.statusTextError}>
              {data.error_message || "An infrastructure error occurred during verification."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
