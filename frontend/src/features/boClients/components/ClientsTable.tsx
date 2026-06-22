"use client";

import Button from "@/components/ui/Button";
import Badge from "@/features/bo/shared/Badge";

import panel from "@/features/bo/shared/panel.module.css";

import { formatChannel, fullName } from "../format";
import type { Client } from "../types";

function StateCell({ client }: { client: Client }) {
  if (client.blacklisted) return <Badge tone="error">Lista negra</Badge>;
  if (!client.is_active) return <Badge tone="neutral">Inativo</Badge>;
  return <Badge tone="success">Ativo</Badge>;
}

export default function ClientsTable({
  clients,
  onView,
}: {
  clients: Client[];
  onView: (client: Client) => void;
}) {
  return (
    <div className={panel.tableWrap}>
      <table className={panel.table}>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Telemóvel</th>
            <th>Email</th>
            <th>Canal</th>
            <th>Estado</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {clients.map((client) => (
            <tr key={client.id}>
              <td>{fullName(client)}</td>
              <td>{client.msisdn}</td>
              <td>{client.email}</td>
              <td>{formatChannel(client.preferred_channel)}</td>
              <td>
                <StateCell client={client} />
              </td>
              <td>
                <div className={panel.actions}>
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => onView(client)}
                  >
                    Ver
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
