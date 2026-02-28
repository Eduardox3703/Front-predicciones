import "./globals.css";

export const metadata = {
  title: "Sistema Inteligente de Predicción",
  description: "Predicción avanzada de asistencia a eventos",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="bg-black text-white min-h-screen font-sans selection:bg-purple-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}