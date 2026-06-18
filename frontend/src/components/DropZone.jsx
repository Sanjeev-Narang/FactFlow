import React, { useState, useRef } from 'react';
import { UploadCloud, AlertCircle } from 'lucide-react';
import styles from './DropZone.module.css';

export default function DropZone({ onFileSelected, isProcessing }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const validateAndProcessFile = (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF documents are supported.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File size cannot exceed 10MB.');
      return;
    }
    setError('');
    onFileSelected(file);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndProcessFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className={styles.wrapper}>
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => !isProcessing && fileInputRef.current.click()}
        className={`${styles.dropzone} 
          ${isDragActive ? styles.active : ''} 
          ${isProcessing ? styles.disabled : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={(e) => e.target.files && validateAndProcessFile(e.target.files[0])}
        />
        
        <UploadCloud className={styles.icon} />
        <h3 className={styles.title}>Choose Files</h3>
        <p className={styles.text}>or drag and drop your PDF here</p>
        <p className={styles.subtext}>Max file size 10MB. Files are verified straight in server RAM.</p>
      </div>

      {error && (
        <div className={styles.errorBox}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
