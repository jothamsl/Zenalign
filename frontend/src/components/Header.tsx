import { useState, useEffect } from "react";
import { ShieldCheck, Coins } from "lucide-react";
import { toast } from "sonner";
import { TokenPurchase } from "./TokenPurchase";
import { senalignAPI } from "../services/api";

// For now, we'll use a hardcoded email. In production, this should come from auth context
const DEFAULT_USER_EMAIL = "user@senalign.com";

export function Header() {
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);
  const [tokenBalance, setTokenBalance] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [isNewUser, setIsNewUser] = useState(false);

  const fetchBalance = async () => {
    try {
      setLoading(true);
      const data = await senalignAPI.getTokenBalance(DEFAULT_USER_EMAIL);

      // Check if this is a new user with free tokens
      const isNew =
        data.token_balance === 100 &&
        data.total_consumed === 0 &&
        data.total_purchased === 100;

      if (isNew && !isNewUser) {
        setIsNewUser(true);
        // Show welcome toast for new users
        toast.success("Welcome to Senalign! 🎉", {
          description:
            "You've received 100 free tokens to get started! That's 10 free dataset analyses.",
          duration: 8000,
        });
      }

      setTokenBalance(data.token_balance);
    } catch (err: any) {
      console.error("Failed to fetch token balance:", err);
      // Set to 0 if fetch fails (new user)
      setTokenBalance(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBalance();
  }, []);

  const handlePurchaseComplete = () => {
    // Show success toast
    toast.success("Tokens Purchased Successfully!", {
      description: "Your tokens have been credited to your account.",
      duration: 4000,
    });
    // Refresh balance after purchase
    fetchBalance();
  };

  const isLowBalance = tokenBalance !== null && tokenBalance < 20;

  return (
    <>
      <header className="w-full px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="bg-black rounded-md p-1.5">
            <ShieldCheck className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold">Zenalign</span>
        </div>

        <div className="flex items-center gap-4">
          {/* Token Balance Display */}
          <button
            onClick={() => setShowPurchaseModal(true)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all hover:scale-105 ${
              isLowBalance
                ? "bg-amber-50 border border-amber-200 text-amber-700 hover:bg-amber-100"
                : "bg-green-50 border border-green-200 text-green-700 hover:bg-green-100"
            }`}
            title="Click to buy tokens"
          >
            <Coins
              className={`w-4 h-4 ${isLowBalance ? "text-amber-600" : "text-green-600"}`}
            />
            <span className="font-semibold text-sm">
              {loading
                ? "..."
                : tokenBalance !== null
                  ? `${tokenBalance} tokens`
                  : "0 tokens"}
            </span>
          </button>
        </div>
      </header>

      {/* Token Purchase Modal */}
      <TokenPurchase
        userEmail={DEFAULT_USER_EMAIL}
        isOpen={showPurchaseModal}
        onClose={() => setShowPurchaseModal(false)}
        onPurchaseComplete={handlePurchaseComplete}
      />
    </>
  );
}
