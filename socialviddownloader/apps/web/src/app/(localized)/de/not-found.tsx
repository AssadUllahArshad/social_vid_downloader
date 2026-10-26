import Link from "next/link";
import { dictionaries } from "@/lib/i18n";
export default function Missing(){const t=dictionaries["de"];return <main className="container content-page"><h1>{t.notFound}</h1><Link href="/de/">{t.back}</Link></main>;}
