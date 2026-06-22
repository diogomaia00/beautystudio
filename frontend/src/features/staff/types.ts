export type EducationType =
  | "formation"
  | "webinar"
  | "course"
  | "workshop"
  | "other";

export interface StaffEducation {
  id: string;
  education_type: EducationType;
  provider: string;
  title: string;
  /** ISO date (YYYY-MM-DD). */
  completed_on: string;
  description: string;
}

/** Public staff representation from `GET /v1/staff/`. */
export interface StaffPublic {
  id: string;
  first_name: string;
  last_name: string;
  educations: StaffEducation[];
}
