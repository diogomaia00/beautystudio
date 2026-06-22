"use client";

import Button from "@/components/ui/Button";
import Badge from "@/features/bo/shared/Badge";
import type { Service } from "@/features/services/types";

import panel from "@/features/bo/shared/panel.module.css";

import { formatDuration, formatPrice } from "../format";

function PriceCell({ service }: { service: Service }) {
  if (service.is_quote_only || service.price === null) {
    return <Badge tone="accent">Sob orçamento</Badge>;
  }
  const base = formatPrice(service.price, false);
  const hasDiscount =
    service.effective_price !== null &&
    service.effective_price !== service.price;
  if (!hasDiscount) return <span>{base}</span>;
  return (
    <span>
      <s>{base}</s> {formatPrice(service.effective_price, false)}
    </span>
  );
}

export default function ServicesTable({
  services,
  onEdit,
  onDiscounts,
}: {
  services: Service[];
  onEdit: (service: Service) => void;
  onDiscounts: (service: Service) => void;
}) {
  return (
    <div className={panel.tableWrap}>
      <table className={panel.table}>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Categoria</th>
            <th>Staff</th>
            <th>Duração</th>
            <th>Preço</th>
            <th>Nail</th>
            <th>Estado</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {services.map((service) => (
            <tr key={service.id}>
              <td>{service.name}</td>
              <td>{service.category.name}</td>
              <td>
                {service.staff.first_name} {service.staff.last_name}
              </td>
              <td>{formatDuration(service.duration_minutes)}</td>
              <td>
                <PriceCell service={service} />
              </td>
              <td>
                {service.is_nail_service ? <Badge tone="info">Nail</Badge> : "—"}
              </td>
              <td>
                {service.is_active ? (
                  <Badge tone="success">Ativo</Badge>
                ) : (
                  <Badge tone="neutral">Inativo</Badge>
                )}
              </td>
              <td>
                <div className={panel.actions}>
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => onEdit(service)}
                  >
                    Editar
                  </Button>
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => onDiscounts(service)}
                  >
                    Descontos
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
