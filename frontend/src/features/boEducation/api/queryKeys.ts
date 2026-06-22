export const boEducationKeys = {
  all: ["bo", "educations"] as const,
  list: (staffId: string) => [...boEducationKeys.all, "list", staffId] as const,
};
