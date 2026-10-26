import Link from "next/link";
import { dictionaries } from "@/lib/i18n";
export default function Missing(){const t=dictionaries["ar"];return <main className="container content-page"><h1>{t.notFound}</h1><Link href="/ar/">{t.back}</Link></main>;}
