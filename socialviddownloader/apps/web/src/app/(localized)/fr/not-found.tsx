import Link from "next/link";
import { dictionaries } from "@/lib/i18n";
export default function Missing(){const t=dictionaries["fr"];return <main className="container content-page"><h1>{t.notFound}</h1><Link href="/fr/">{t.back}</Link></main>;}
