"use client";

import { useState } from "react";

import Button from "@/components/ui/Button";
import Field from "@/components/ui/Field";
import Input from "@/components/ui/Input";
import PageHeader from "@/components/layouts/PageHeader";
import ClientDetailModal from "@/features/boClients/components/ClientDetailModal";
import ClientsTable from "@/features/boClients/components/ClientsTable";
import { useClients } from "@/features/boClients/hooks/useClients";
import type { Client } from "@/features/boClients/types";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/features/bo/shared/States";
import { apiErrorMessage } from "@/lib/api";

import panel from "@/features/bo/shared/panel.module.css";

export default function BoClientesPage() {
  const [term, setTerm] = useState("");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Client | null>(null);

  const clients = useClients(search);

  const onSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSearch(term.trim());
  };

  return (
    <div className={panel.page}>
      <PageHeader
        title="Clientes"
        subtitle="Gere os clientes, consulta o histórico de presenças, a lista negra e as durações personalizadas por serviço."
      />

      <form className={panel.toolbar} onSubmit={onSearch}>
        <Field label="Pesquisar" htmlFor="clients-search">
          <Input
            id="clients-search"
            type="search"
            placeholder="Nome, telemóvel ou email"
            value={term}
            onChange={(event) => setTerm(event.target.value)}
          />
        </Field>
        <div className={panel.toolbarPush}>
          <Button type="submit">Pesquisar</Button>
        </div>
      </form>

      {clients.isLoading ? (
        <LoadingState label="A carregar clientes…" />
      ) : clients.isError ? (
        <ErrorState
          action={
            <Button
              type="button"
              variant="secondary"
              onClick={() => clients.refetch()}
            >
              Tentar novamente
            </Button>
          }
        >
          {apiErrorMessage(clients.error, "Não foi possível carregar os clientes.")}
        </ErrorState>
      ) : (clients.data ?? []).length === 0 ? (
        <EmptyState title="Sem clientes">
          {search
            ? "Nenhum cliente corresponde à pesquisa."
            : "Ainda não existem clientes registados."}
        </EmptyState>
      ) : (
        <ClientsTable
          clients={clients.data ?? []}
          onView={(client) => setSelected(client)}
        />
      )}

      {selected ? (
        <ClientDetailModal
          client={selected}
          onClose={() => setSelected(null)}
        />
      ) : null}
    </div>
  );
}
