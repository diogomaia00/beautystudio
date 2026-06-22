"use client";

import { createContext, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { useCurrentUser } from "@/features/auth/hooks/useCurrentUser";
import { useStaff } from "@/features/staff/hooks/useStaff";

export interface StaffOption {
  id: string;
  first_name: string;
  last_name: string;
}

interface ActiveStaffValue {
  /** Staff member the BO pages currently operate on (null while resolving). */
  staffId: string | null;
  /** Selectable staff (admin only; staff see just themselves). */
  staffList: StaffOption[];
  /** Change the active staff member (admin only). */
  setStaffId: (id: string) => void;
  /** True when the signed-in user is the admin (can switch staff). */
  isAdmin: boolean;
  isLoading: boolean;
}

const ActiveStaffContext = createContext<ActiveStaffValue | null>(null);

/**
 * Resolves the "active staff" for back-office pages scoped to a single staff
 * member (schedule, agenda, waitlist, ...). A staff user always operates on
 * their own id; the admin gets a picker populated from the public staff list.
 */
export function ActiveStaffProvider({ children }: { children: ReactNode }) {
  const { data: user, isLoading: userLoading } = useCurrentUser();
  const isAdmin = user?.role === "admin";

  // The admin needs the full staff roster to pick from; staff don't.
  const { data: staff, isLoading: staffLoading } = useStaff(isAdmin);
  const [selected, setSelected] = useState<string | null>(null);

  const value = useMemo<ActiveStaffValue>(() => {
    if (isAdmin) {
      const list = (staff ?? []).map((s) => ({
        id: s.id,
        first_name: s.first_name,
        last_name: s.last_name,
      }));
      return {
        staffId: selected ?? list[0]?.id ?? null,
        staffList: list,
        setStaffId: setSelected,
        isAdmin: true,
        isLoading: userLoading || staffLoading,
      };
    }

    // Staff member: operate on their own id, no picker.
    const self: StaffOption[] = user
      ? [{ id: user.id, first_name: user.first_name, last_name: user.last_name }]
      : [];
    return {
      staffId: user?.id ?? null,
      staffList: self,
      setStaffId: () => undefined,
      isAdmin: false,
      isLoading: userLoading,
    };
  }, [isAdmin, staff, selected, user, userLoading, staffLoading]);

  return (
    <ActiveStaffContext.Provider value={value}>
      {children}
    </ActiveStaffContext.Provider>
  );
}

/** Read the active-staff context. Must be used inside `ActiveStaffProvider`. */
export function useActiveStaff(): ActiveStaffValue {
  const ctx = useContext(ActiveStaffContext);
  if (!ctx) {
    throw new Error("useActiveStaff must be used within ActiveStaffProvider");
  }
  return ctx;
}
