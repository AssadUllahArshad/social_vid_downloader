import { GuideCollection, collectionPaths, collectionMetadata } from "@/components/guide-collection";
type Props = { params: Promise<{ family: string }> };
export function generateStaticParams() { return collectionPaths("family").filter(row => row.number === "1").map(row => ({ family: row.key })); }
export async function generateMetadata({ params }: Props) {
  const { family } = await params;
  return collectionMetadata("family", family);
}
export default async function Directory({ params }: Props) {
  const { family } = await params;
  return <GuideCollection kind="family" group={family} />;
}
