import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createEducation,
  deleteEducation,
  updateEducation,
} from "../api/mutations";
import { fetchEducations } from "../api/queries";
import { boEducationKeys } from "../api/queryKeys";
import type { CreateEducationInput, UpdateEducationInput } from "../types";

/** List a staff member's educations. Disabled until `staffId` is known. */
export function useEducations(staffId: string | null) {
  return useQuery({
    queryKey: boEducationKeys.list(staffId ?? ""),
    queryFn: () => fetchEducations(staffId ?? ""),
    staleTime: 60_000,
    enabled: !!staffId,
  });
}

export function useCreateEducation(staffId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateEducationInput) =>
      createEducation(staffId, input),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: boEducationKeys.list(staffId),
      }),
  });
}

export function useUpdateEducation(staffId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: UpdateEducationInput }) =>
      updateEducation(staffId, id, input),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: boEducationKeys.list(staffId),
      }),
  });
}

export function useDeleteEducation(staffId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteEducation(staffId, id),
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: boEducationKeys.list(staffId),
      }),
  });
}
