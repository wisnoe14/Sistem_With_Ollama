const PageTransition = ({ show }: { show: boolean }) => {
  if (!show) return null;
  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-gradient-to-br from-blue-100 to-purple-200 bg-opacity-90">
      <img src="/public/vite.svg" alt="Memuat" className="w-28 h-28 animate-bounce mb-6" />
    </div>
  );
};

export default PageTransition;
