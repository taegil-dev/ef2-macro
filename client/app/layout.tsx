import "./globals.css";
export const metadata = {
  title: "MacroDeck — Remote Control",
  description: "Private remote game macro controller",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
