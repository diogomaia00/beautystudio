"use client";

import { useState } from "react";

import BookingPanel from "@/features/appointments/components/BookingPanel";

import { contactForCategory } from "../config";
import { formatDuration, formatPrice } from "../format";
import { useCategories, useServices } from "../hooks/useCatalog";
import type { Service, ServiceCategory } from "../types";
import styles from "./SchedulingTabs.module.css";

function CategoryPanel({ category }: { category: ServiceCategory }) {
  const { data: services, isLoading, isError } = useServices(category.id);
  const [openId, setOpenId] = useState<string | null>(null);
  const contact = contactForCategory(category.slug);
  const bookable = !contact;

  if (isLoading) return <p className={styles.status}>A carregar serviços…</p>;
  if (isError)
    return <p className={styles.contactNotice}>Não foi possível carregar os serviços.</p>;
  if (!services || services.length === 0)
    return <p className={styles.status}>Sem serviços nesta categoria.</p>;

  return (
    <div className={styles.panel}>
      {bookable ? (
        <p className={styles.bookableHint} role="note">
          Escolhe um serviço e agenda online. Precisas de ter sessão iniciada.
        </p>
      ) : (
        <p className={styles.contactNotice} role="note">
          A <strong>{category.name}</strong> não tem agendamento online. Para
          marcações, contacta diretamente o <strong>{contact.staffName}</strong>{" "}
          através do{" "}
          <a href={`tel:${contact.phone.replace(/\s/g, "")}`}>{contact.phone}</a>.
        </p>
      )}

      <ul className={styles.list}>
        {services.map((service: Service) => {
          const isOpen = openId === service.id;
          return (
            <li key={service.id} className={styles.row}>
              <div className={styles.rowLine}>
                <div className={styles.rowMain}>
                  <span className={styles.serviceName}>{service.name}</span>
                  {bookable && (
                    <span className={styles.duration}>
                      {formatDuration(service.duration_minutes)}
                    </span>
                  )}
                </div>
                <div className={styles.rowEnd}>
                  <span className={styles.price}>
                    {formatPrice(service.effective_price, service.is_quote_only)}
                  </span>
                  {bookable && (
                    <button
                      type="button"
                      className={styles.bookButton}
                      aria-expanded={isOpen}
                      onClick={() => setOpenId(isOpen ? null : service.id)}
                    >
                      {isOpen ? "Fechar" : "Agendar"}
                    </button>
                  )}
                </div>
              </div>
              {bookable && isOpen && <BookingPanel service={service} />}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default function SchedulingTabs() {
  const { data: categories, isLoading, isError } = useCategories();
  const [picked, setPicked] = useState<string | null>(null);

  if (isLoading) return <p className={styles.status}>A carregar categorias…</p>;
  if (isError)
    return (
      <p className={styles.contactNotice}>
        Não foi possível carregar as categorias. Tenta novamente mais tarde.
      </p>
    );
  if (!categories || categories.length === 0)
    return <p className={styles.status}>Catálogo indisponível de momento.</p>;

  const activeSlug = picked ?? categories[0].slug;
  const active = categories.find((c) => c.slug === activeSlug) ?? categories[0];

  return (
    <div>
      <div className={styles.tabs} role="tablist" aria-label="Categorias de serviços">
        {categories.map((category) => {
          const selected = category.slug === active.slug;
          return (
            <button
              key={category.slug}
              type="button"
              role="tab"
              aria-selected={selected}
              className={styles.tab}
              data-active={selected || undefined}
              onClick={() => setPicked(category.slug)}
            >
              {category.name}
            </button>
          );
        })}
      </div>

      <div className={styles.panelWrap} role="tabpanel">
        <CategoryPanel key={active.id} category={active} />
      </div>
    </div>
  );
}
