import "./globals.css";
import "./responsive.css";

export const metadata = {
  title: "ef2 — Remote Control",
  description: "Private remote game macro controller",
};

export default function RootLayout({ children, }: { children: React.ReactNode; }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
