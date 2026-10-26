import { notFound } from "next/navigation";

// Administration is a development-only read-only shell. A production CMS/auth
// system does not exist; never publish editorial planning data as an admin UI.
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  if (process.env.NODE_ENV === "production") notFound();
  return children;
}
