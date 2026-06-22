import { CLINIC } from "@/shared/constants/site";

import styles from "./Footer.module.css";

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        <span className={styles.name}>{CLINIC.name}</span>
        <address className={styles.address}>{CLINIC.location}</address>
      </div>
    </footer>
  );
}
