import type { Metadata } from "next";

import PageHeader from "@/components/layouts/PageHeader";

import styles from "./servicos.module.css";

export const metadata: Metadata = {
  title: "Serviços — Beauty Studio",
};

// Placeholder blocks — real copy and images are added later in the BO / CMS.
const PLACEHOLDERS = [
  { id: "unhas", label: "Unhas" },
  { id: "estetica", label: "Estética" },
  { id: "laser", label: "Depilação Laser" },
];

export default function ServicesPage() {
  return (
    <div>
      <PageHeader
        title="Serviços"
        subtitle="Descrições e fotografias dos nossos serviços — em breve."
      />

      <div className={styles.grid}>
        {PLACEHOLDERS.map((item) => (
          <article key={item.id} className={styles.card}>
            <div className={styles.image} aria-hidden="true">
              <span className={styles.imageLabel}>Imagem em breve</span>
            </div>
            <div className={styles.body}>
              <h2 className={styles.cardTitle}>{item.label}</h2>
              <div className={styles.textLines} aria-hidden="true">
                <span className={styles.line} />
                <span className={styles.line} />
                <span className={`${styles.line} ${styles.lineShort}`} />
              </div>
              <p className={styles.note}>Descrição a adicionar.</p>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
