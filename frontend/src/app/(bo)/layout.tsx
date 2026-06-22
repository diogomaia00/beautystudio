import { ActiveStaffProvider } from "@/features/bo/shared/ActiveStaffContext";

import BoGuard from "./BoGuard";
import Sidebar from "./Sidebar";
import styles from "./bo.module.css";

export default function BackOfficeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <BoGuard>
      <ActiveStaffProvider>
        <div className={styles.shell}>
          <Sidebar />
          <main className={styles.main}>{children}</main>
        </div>
      </ActiveStaffProvider>
    </BoGuard>
  );
}
