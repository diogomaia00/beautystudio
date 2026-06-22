import Link from "next/link";

import Button from "@/components/ui/Button";
import { NAV_LINKS } from "@/shared/constants/site";

import styles from "./home.module.css";

export default function HomePage() {
  const quickLinks = NAV_LINKS.filter((link) => link.href !== "/");

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className={styles.eyebrow}>Beauty Studio</p>
        <h1 className={styles.title}>Cuidamos de ti, da cabeça às unhas</h1>
        <p className={styles.lead}>
          Unhas, estética e depilação a laser num só espaço. 
          Marca o teu momento de cuidado e deixa o resto connosco.
        </p>
        <div className={styles.actions}>
          <Button href="/agendar" size="lg">
            Agendar
          </Button>
        </div>
      </section>

      <nav className={styles.cards} aria-label="Páginas">
        {quickLinks.map((link) => (
          <Link key={link.href} href={link.href} className={styles.card}>
            <span className={styles.cardLabel}>{link.label}</span>
          </Link>
        ))}
      </nav>
    </div>
  );
}
