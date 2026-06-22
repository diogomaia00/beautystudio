/** A seasonal percentage discount on a service (BO-managed). */
export interface ServiceDiscount {
  id: string;
  service: string;
  /** Decimal string, e.g. "10.00". */
  percentage: string;
  /** ISO datetime (UTC). */
  starts_at: string;
  /** ISO datetime (UTC). */
  ends_at: string;
  is_active: boolean;
}

/** Body for `POST /bo/v1/services/`. */
export interface CreateServiceInput {
  category_id: string;
  staff_id: string;
  name: string;
  description?: string;
  duration_minutes: number;
  /** Decimal string or null (price on request). */
  price?: string | null;
  is_quote_only?: boolean;
  is_nail_service?: boolean;
  is_active?: boolean;
}

/** Partial body for `PATCH /bo/v1/services/{id}/`. */
export type UpdateServiceInput = Partial<CreateServiceInput>;

/** Body for `POST /bo/v1/services/{id}/discounts/`. */
export interface CreateDiscountInput {
  /** Number or decimal string. */
  percentage: number | string;
  /** ISO datetime. */
  starts_at: string;
  /** ISO datetime. */
  ends_at: string;
}
