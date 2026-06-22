import Footer from "@/components/layouts/Footer";
import Navbar from "@/components/layouts/Navbar";

import styles from "./layout.module.css";

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className={styles.shell}>
      <Navbar />
      <main className={styles.main}>{children}</main>
      <Footer />
    </div>
  );
}
