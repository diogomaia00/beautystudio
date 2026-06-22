"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Select from "@/components/ui/Select";
import PageHeader from "@/components/layouts/PageHeader";
import DiscountsModal from "@/features/boServices/components/DiscountsModal";
import ServiceFormModal from "@/features/boServices/components/ServiceFormModal";
import ServicesTable from "@/features/boServices/components/ServicesTable";
import { useBoServices } from "@/features/boServices/hooks/useBoServices";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/features/bo/shared/States";
import { useCategories } from "@/features/services/hooks/useCatalog";
import type { Service } from "@/features/services/types";
import { apiErrorMessage } from "@/lib/api";

import panel from "@/features/bo/shared/panel.module.css";

type ModalState =
  | { kind: "none" }
  | { kind: "create" }
  | { kind: "edit"; service: Service }
  | { kind: "discounts"; service: Service };

export default function BoServicosPage() {
  const [categoryId, setCategoryId] = useState("");
  const [activeOnly, setActiveOnly] = useState(false);
  const [modal, setModal] = useState<ModalState>({ kind: "none" });

  const categories = useCategories();
  const services = useBoServices({
    categoryId: categoryId || undefined,
    activeOnly,
  });

  const closeModal = () => setModal({ kind: "none" });

  return (
    <div className={panel.page}>
      <PageHeader
        title="Serviços"
        subtitle="Gere os serviços oferecidos, os preços, os pedidos sob orçamento e os descontos sazonais."
      />

      <div className={panel.toolbar}>
        <Field label="Categoria" htmlFor="filter-category">
          <Select
            id="filter-category"
            value={categoryId}
            disabled={categories.isLoading}
            onChange={(event) => setCategoryId(event.target.value)}
          >
            <option value="">Todas as categorias</option>
            {(categories.data ?? []).map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </Select>
        </Field>

        <label>
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(event) => setActiveOnly(event.target.checked)}
          />{" "}
          Apenas ativos
        </label>

        <div className={panel.toolbarPush}>
          <Button type="button" onClick={() => setModal({ kind: "create" })}>
            Novo serviço
          </Button>
        </div>
      </div>

      {services.isLoading ? (
        <LoadingState label="A carregar serviços…" />
      ) : services.isError ? (
        <ErrorState
          action={
            <Button type="button" variant="secondary" onClick={() => services.refetch()}>
              Tentar novamente
            </Button>
          }
        >
          {apiErrorMessage(services.error, "Não foi possível carregar os serviços.")}
        </ErrorState>
      ) : (services.data ?? []).length === 0 ? (
        <EmptyState
          title="Sem serviços"
          action={
            <Button type="button" onClick={() => setModal({ kind: "create" })}>
              Novo serviço
            </Button>
          }
        >
          Ainda não existem serviços com estes filtros.
        </EmptyState>
      ) : (
        <ServicesTable
          services={services.data ?? []}
          onEdit={(service) => setModal({ kind: "edit", service })}
          onDiscounts={(service) => setModal({ kind: "discounts", service })}
        />
      )}

      {modal.kind === "create" ? (
        <ServiceFormModal onClose={closeModal} />
      ) : null}

      {modal.kind === "edit" ? (
        <ServiceFormModal service={modal.service} onClose={closeModal} />
      ) : null}

      {modal.kind === "discounts" ? (
        <DiscountsModal service={modal.service} onClose={closeModal} />
      ) : null}
    </div>
  );
}
