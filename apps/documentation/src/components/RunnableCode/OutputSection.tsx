import React from "react";

import styles from "./styles.module.css";

function OutputSection({ children, minHeight = "" }) {
  return (
    <div className={styles.browserWindow} style={{ minHeight }}>
      <div className={styles.browserWindowBody}>{children}</div>
    </div>
  );
}

export default OutputSection;
