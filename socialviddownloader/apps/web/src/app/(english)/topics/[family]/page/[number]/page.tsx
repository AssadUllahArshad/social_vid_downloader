import { GuideCollection, collectionPaths, collectionMetadata } from "@/components/guide-collection";
type Props = { params: Promise<{ family: string; number: string }> };
export function generateStaticParams() { return collectionPaths("family").filter(row => row.number !== "1").map(row => ({ family: row.key, number: row.number })); }
export async function generateMetadata({ params }: Props) {
  const { family, number } = await params;
  return collectionMetadata("family", family, number, true);
}
export default async function Directory({ params }: Props) {
  const { family, number } = await params;
  collectionMetadata("family", family, number, true);
  return <GuideCollection kind="family" group={family} number={Number(number)} />;
}
