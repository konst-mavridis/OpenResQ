import Link from "next/link";
import type { ReactNode } from "react";
import PublicLegalFooter from "./PublicLegalFooter";
import ThemeToggle from "../ThemeToggle";

interface LegalPageShellProps {
  title: string;
  summary: string;
  effectiveDate: string;
  children: ReactNode;
}

export default function LegalPageShell({
  title,
  summary,
  effectiveDate,
  children,
}: LegalPageShellProps) {
  return (
    <main className="min-h-screen bg-(--background) text-(--foreground) sm:px-6 lg:px-8 px-4 py-8 bg-[radial-gradient(circle_at_top,_rgba(37,99,235,0.05),_transparent_40%)]">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex items-center justify-between px-1 text-sm text-foreground/60">
          <Link href="/login" className="transition hover:text-foreground">
            Back to login
          </Link>
          <div className="flex items-center gap-4">
            <div className="hidden items-center gap-3 text-xs uppercase tracking-[0.25em] text-foreground/40 sm:flex">
              <span>OpenResQ</span>
              <span className="h-px w-8 bg-border" />
              <span>Legal Document</span>
            </div>
            <ThemeToggle />
          </div>
        </div>

        <article className="overflow-hidden rounded-[2rem] border border-border bg-(--background) text-foreground shadow-[0_24px_80px_rgba(0,0,0,0.12)] dark:shadow-[0_24px_80px_rgba(0,0,0,0.45)]">
          <div className="border-b border-border bg-foreground/[0.02] px-6 py-8 sm:px-10 sm:py-10">
            <div className="mb-6 flex flex-wrap items-center gap-3">
              <span className="rounded-full border border-border bg-foreground/[0.03] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-foreground/70">
                OpenResQ Legal
              </span>
              <span className="rounded-full border border-border/80 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-foreground/50">
                Effective {effectiveDate}
              </span>
            </div>

            <div className="grid gap-6 sm:grid-cols-[minmax(0,1fr)_220px] sm:items-end">
              <div className="space-y-4">
                <h1 className="font-serif text-4xl leading-tight tracking-tight sm:text-5xl text-foreground">
                  {title}
                </h1>
                <p className="max-w-2xl text-base leading-7 text-foreground/80">
                  {summary}
                </p>
              </div>

              <div className="rounded-2xl border border-border bg-foreground/[0.01] p-4 text-sm text-foreground/60">
                <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-foreground/40">
                  Document Details
                </p>
                <dl className="mt-3 space-y-2">
                  <div className="flex items-start justify-between gap-3">
                    <dt>Type</dt>
                    <dd className="font-medium text-foreground">{title}</dd>
                  </div>
                  <div className="flex items-start justify-between gap-3">
                    <dt>Status</dt>
                    <dd className="font-medium text-foreground">Active</dd>
                  </div>
                  <div className="flex items-start justify-between gap-3">
                    <dt>Applies to</dt>
                    <dd className="text-right font-medium text-foreground">Dashboard Services</dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>

          <div className="px-6 py-8 sm:px-10 sm:py-12 bg-(--background)">
            <div className="mx-auto max-w-3xl space-y-8 font-serif text-[17px] leading-8 text-foreground/90 [&_h2]:mt-12 [&_h2]:border-b [&_h2]:border-border/60 [&_h2]:pb-3 [&_h2]:font-sans [&_h2]:text-xl [&_h2]:font-semibold [&_h2]:tracking-tight [&_p]:my-4 [&_ul]:my-5 [&_ul]:list-disc [&_ul]:space-y-3 [&_ul]:pl-6 [&_li]:pl-1 [&_strong]:font-semibold [&_a]:text-primary [&_a]:underline [&_a]:decoration-primary/30 [&_a]:underline-offset-4 hover:[&_a]:decoration-primary transition-all">
              {children}
            </div>
          </div>

          <div className="border-t border-border bg-foreground/[0.02] px-6 py-6 sm:px-10">
            <PublicLegalFooter />
          </div>
        </article>
      </div>
    </main>
  );
}
