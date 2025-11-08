import { ShieldCheck } from 'lucide-react';

export function Header() {
  return (
    <header className="w-full px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="bg-black rounded-md p-1.5">
          <ShieldCheck className="w-4 h-4 text-white" />
        </div>
        <span className="font-semibold">Senalign</span>
      </div>
      
      <div className="flex items-center gap-4">
        <button className="text-sm hover:opacity-70 transition-opacity">
          Log In
        </button>
      </div>
    </header>
  );
}
