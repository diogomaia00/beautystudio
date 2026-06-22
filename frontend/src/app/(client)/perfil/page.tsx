import type { Metadata } from "next";

import PageHeader from "@/components/layouts/PageHeader";
import ProfileForm from "@/features/profile/components/ProfileForm";

export const metadata: Metadata = {
  title: "Perfil — Beauty Studio",
};

export default function ProfilePage() {
  return (
    <div>
      <PageHeader title="Perfil" subtitle="Os teus dados e canal de contacto preferido." />
      <ProfileForm />
    </div>
  );
}
