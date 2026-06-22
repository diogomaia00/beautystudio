import type { EducationType } from "@/features/staff/types";

/** pt-PT labels for each education type, in display order. */
export const EDUCATION_TYPES: ReadonlyArray<{
  value: EducationType;
  label: string;
}> = [
  { value: "formation", label: "Formação" },
  { value: "webinar", label: "Webinar" },
  { value: "course", label: "Curso" },
  { value: "workshop", label: "Workshop" },
  { value: "other", label: "Outro" },
];

/** Body for creating an education entry. */
export interface CreateEducationInput {
  education_type?: EducationType;
  provider: string;
  title: string;
  /** YYYY-MM-DD. */
  completed_on: string;
  description?: string;
}

/** Partial body for updating an education entry. */
export type UpdateEducationInput = Partial<CreateEducationInput>;
