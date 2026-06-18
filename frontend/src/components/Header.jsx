import React from 'react';
import { ShieldCheck, FileCheck } from 'lucide-react';
import styles from './Header.module.css';

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        {/* Brand Logo Grouping */}
        <div className={styles.logo}>
          <ShieldCheck size={24} className={styles.logoHighlight} />
          <span>Fact<span className={styles.logoHighlight}>Flow</span>AI</span>
        </div>
        
        {/* Stateless Architecture Indicator Badge */}
        <div>
          <div className={styles.badge}>
            <FileCheck size={16} />
            <span>Stateless RAM Processing</span>
          </div>
        </div>
      </div>
    </header>
  );
}
