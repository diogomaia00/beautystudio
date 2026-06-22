export interface ServiceCategory {
  id: string;
  name: string;
  slug: string;
  description: string;
  display_order: number;
}

export interface StaffBrief {
  id: string;
  first_name: string;
  last_name: string;
}

export interface Service {
  id: string;
  name: string;
  description: string;
  category: ServiceCategory;
  staff: StaffBrief;
  duration_minutes: number;
  /** Decimal string or null (price on request). */
  price: string | null;
  /** Effective price after any active discount; string or null. */
  effective_price: string | null;
  is_quote_only: boolean;
  is_nail_service: boolean;
  is_active: boolean;
}
