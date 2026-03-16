/**
 * Root layout component for Next.js app
 */
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Hita - Your Personal Document Assistant',
  description: 'Your personal document vault app for managing bills, medical records, and more',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900">
        {children}
      </body>
    </html>
  );
}
