import React from 'react';
import styles from '../styles/components.module.css';

export const GeneratingIndicator: React.FC = () => {
  return (
    <div className={styles.typingIndicator}>
      <div className={styles.typingDot}></div>
      <div className={styles.typingDot}></div>
      <div className={styles.typingDot}></div>
    </div>
  );
};