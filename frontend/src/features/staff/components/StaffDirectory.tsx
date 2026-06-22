"use client";

import Button from "@/components/ui/Button";

import type { EducationType, StaffEducation } from "../types";
import { useStaff } from "../hooks/useStaff";

import styles from "./StaffDirectory.module.css";

const EDUCATION_LABELS: Record<EducationType, string> = {
  formation: "Formação",
  webinar: "Webinar",
  course: "Curso",
  workshop: "Workshop",
  other: "Outro",
};

function Formations({ educations }: { educations: StaffEducation[] }) {
  if (educations.length === 0) {
    return <p className={styles.empty}>Formações a adicionar.</p>;
  }
  return (
    <ul className={styles.formations}>
      {educations.map((edu) => (
        <li key={edu.id} className={styles.formation}>
          <div className={styles.formationHead}>
            <span className={styles.formationTitle}>{edu.title}</span>
            <span className={styles.formationTag}>
              {EDUCATION_LABELS[edu.education_type]}
            </span>
          </div>
          <span className={styles.formationMeta}>
            {edu.provider}
            {edu.completed_on ? ` · ${edu.completed_on.slice(0, 4)}` : ""}
          </span>
          {edu.description && (
            <p className={styles.formationDesc}>{edu.description}</p>
          )}
        </li>
      ))}
    </ul>
  );
}

export default function StaffDirectory() {
  const { data, isLoading, isError, refetch } = useStaff();

  if (isLoading) {
    return <p className={styles.status}>A carregar a equipa…</p>;
  }

  if (isError) {
    return (
      <div className={styles.status}>
        <p>Não foi possível carregar a equipa.</p>
        <Button size="sm" variant="secondary" onClick={() => refetch()}>
          Tentar novamente
        </Button>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return <p className={styles.status}>A nossa equipa será anunciada em breve.</p>;
  }

  return (
    <div className={styles.grid}>
      {data.map((member) => (
        <article key={member.id} className={styles.card}>
          <div className={styles.photo} aria-hidden="true">
            <span className={styles.photoLabel}>Foto em breve</span>
          </div>

          <div className={styles.body}>
            <h2 className={styles.name}>
              {member.first_name} {member.last_name}
            </h2>

            <section className={styles.section}>
              <h3 className={styles.sectionTitle}>Apresentação</h3>
              <p className={styles.empty}>Apresentação a adicionar.</p>
            </section>

            <section className={styles.section}>
              <h3 className={styles.sectionTitle}>Formações</h3>
              <Formations educations={member.educations} />
            </section>
          </div>
        </article>
      ))}
    </div>
  );
}
