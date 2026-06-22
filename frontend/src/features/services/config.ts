/**
 * Front-end booking config not derivable from the catalog API.
 *
 * Some categories are display-only (no online booking) and instruct the client
 * to contact the staff member directly — currently Depilação Laser (João Veloso).
 * Staff phone numbers aren't exposed by the public catalog API, so they live
 * here. Keep in sync with the studio's contacts.
 */
export interface ContactInfo {
  staffName: string;
  phone: string;
}

export const NON_BOOKABLE_CONTACTS: Record<string, ContactInfo> = {
  "depilacao-laser": {
    staffName: "João Veloso",
    phone: "+351 910 028 444",
  },
};

export function contactForCategory(slug: string): ContactInfo | null {
  return NON_BOOKABLE_CONTACTS[slug] ?? null;
}
