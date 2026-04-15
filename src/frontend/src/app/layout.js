import './globals.css';

export const metadata = {
  title: 'Trace Viewer',
  description: 'Time-series data viewer',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}