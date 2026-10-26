import Link from "next/link";
import { dictionaries } from "@/lib/i18n";
export default function Missing(){const t=dictionaries["es"];return <main className="container content-page"><h1>{t.notFound}</h1><Link href="/es/">{t.back}</Link></main>;}
