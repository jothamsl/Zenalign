import { useState, useEffect } from "react";
import { ChevronDown, ArrowRight, X, Coins } from "lucide-react";
import { toast } from "sonner";
import { senalignAPI } from "../services/api";

interface TokenPurchaseProps {
  userEmail: string;
  isOpen: boolean;
  onClose: () => void;
  onPurchaseComplete?: () => void;
}

const tokenAmounts = [500, 1000, 2000, 5000, 10000, 20000];

export const TokenPurchase: React.FC<TokenPurchaseProps> = ({
  userEmail,
  isOpen,
  onClose,
  onPurchaseComplete,
}) => {
  const [selectedAmount, setSelectedAmount] = useState(1000);
  const [loading, setLoading] = useState(false);
  const [pricing, setPricing] = useState<any>(null);

  const nairaRate = 0.5; // ₦0.50 per token (2 tokens per ₦1)

  const calculateNaira = (tokens: number) => {
    return (tokens * nairaRate).toFixed(2);
  };

  const calculateAnalyses = (tokens: number) => {
    return Math.floor(tokens / 10); // 10 tokens per analysis
  };

  // Fetch pricing on mount
  useEffect(() => {
    if (isOpen) {
      fetchPricing();
    }
  }, [isOpen]);

  const fetchPricing = async () => {
    try {
      const data = await senalignAPI.getPricing();
      setPricing(data);
    } catch (err) {
      console.error("Failed to fetch pricing:", err);
    }
  };

  // Close modal on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  const handlePurchase = async () => {
    setLoading(true);

    try {
      const tokens = selectedAmount;
      const amount = parseFloat(calculateNaira(tokens));
      const response = await senalignAPI.purchaseTokens(tokens, userEmail);

      // Open Interswitch payment page in new window
      const paymentWindow = window.open(
        response.payment_url,
        "InterswitchPayment",
        "width=800,height=600,scrollbars=yes,resizable=yes",
      );

      // Poll for payment verification
      pollPaymentStatus(response.transaction_reference, paymentWindow);
    } catch (err: any) {
      console.error("Purchase failed:", err);
      toast.error("Purchase Failed", {
        description: err.response?.data?.detail || "Failed to initiate payment",
      });
      setLoading(false);
    }
  };

  const pollPaymentStatus = (txnRef: string, paymentWindow: Window | null) => {
    const pollInterval = setInterval(async () => {
      // Check if payment window is closed
      if (paymentWindow && paymentWindow.closed) {
        clearInterval(pollInterval);
        await verifyPayment(txnRef);
      }
    }, 2000);

    // Stop polling after 10 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      if (loading) {
        toast.error("Payment Timeout", {
          description:
            "Payment verification timeout. Please check your balance.",
        });
        setLoading(false);
      }
    }, 600000);
  };

  const verifyPayment = async (txnRef: string) => {
    try {
      const result = await senalignAPI.verifyPayment(txnRef);

      if (result.status === "successful") {
        toast.success("Payment Successful!", {
          description: `${result.tokens_credited} tokens have been credited to your account.`,
        });
        setLoading(false);
        if (onPurchaseComplete) {
          onPurchaseComplete();
        }
        onClose();
      } else if (result.status === "pending") {
        toast.info("Payment Pending", {
          description: "Payment is pending. Please try verifying again later.",
        });
        setLoading(false);
      } else {
        toast.error("Payment Failed", {
          description: `Payment ${result.status}. Please try again.`,
        });
        setLoading(false);
      }
    } catch (err: any) {
      console.error("Verification failed:", err);
      toast.error("Verification Failed", {
        description: "Failed to verify payment. Please check your balance.",
      });
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop with blur */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => !loading && onClose()}
      />

      {/* Modal Content */}
      <div className="relative z-50 w-full max-w-[440px] mx-4 bg-gradient-to-br from-green-50 via-blue-50 to-indigo-50 rounded-2xl border border-gray-300 shadow-2xl animate-in fade-in zoom-in duration-200">
        {/* Close Button */}
        <button
          onClick={() => !loading && onClose()}
          disabled={loading}
          className="absolute top-4 right-4 p-1 rounded-lg hover:bg-white/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>

        {/* Header with Logo */}
        <div className="p-8 pb-5">
          <div className="flex justify-center">
            <div className="flex items-center gap-2">
              <Coins className="w-8 h-8 text-blue-600" />
              <span
                className="text-gray-900"
                style={{
                  fontSize: "32px",
                  fontWeight: "bold",
                  letterSpacing: "-0.02em",
                }}
              >
                Senalign
              </span>
            </div>
          </div>
        </div>

        {/* Tab - Only Purchase */}
        <div className="px-8 border-b border-gray-300">
          <div className="inline-block pb-3 border-b-[3px] border-blue-500">
            <span className="text-gray-900">Purchase Tokens</span>
          </div>
        </div>

        {/* Main Content */}
        <div className="px-8 py-8 space-y-7">
          {/* Amount Display */}
          <div className="text-center space-y-1.5">
            <div
              className="text-gray-900"
              style={{
                fontSize: "40px",
                fontWeight: "700",
                letterSpacing: "-0.02em",
              }}
            >
              {selectedAmount.toLocaleString()} tokens
            </div>
            <div className="text-sm text-gray-500">
              ~ ₦{calculateNaira(selectedAmount)} NGN
            </div>
            <div className="text-xs text-gray-400">
              ≈ {calculateAnalyses(selectedAmount)} analyses
            </div>
          </div>

          {/* Token Selection */}
          <div>
            <p className="text-sm text-gray-700 text-center mb-4">
              Select token amount
            </p>
            <div className="grid grid-cols-3 gap-2.5">
              {tokenAmounts.map((amount) => (
                <button
                  key={amount}
                  onClick={() => setSelectedAmount(amount)}
                  disabled={loading}
                  className={`py-3.5 px-2 rounded-xl border-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                    selectedAmount === amount
                      ? "bg-blue-50 border-blue-500 text-blue-700 shadow-sm"
                      : "bg-white/80 border-gray-300 text-gray-700 hover:border-gray-400 hover:bg-white"
                  }`}
                >
                  <div className="text-sm font-semibold">
                    {amount.toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-500">
                    ₦{calculateNaira(amount)}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Pricing Info */}
          <div className="flex items-center justify-between bg-white/60 rounded-xl p-4 border border-gray-200">
            <div>
              <div className="text-gray-900 font-semibold">Exchange Rate</div>
              <div className="text-xs text-gray-500">2 tokens per ₦1</div>
            </div>
            <button className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-gray-300 hover:bg-gray-50 transition-colors shadow-sm">
              <div className="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center text-white text-xs font-bold">
                ₦
              </div>
              <span className="text-sm text-gray-900">NGN</span>
              <ChevronDown className="w-4 h-4 text-gray-500" />
            </button>
          </div>

          {/* Continue Purchase Button */}
          <button
            onClick={handlePurchase}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3.5 rounded-xl transition-colors flex items-center justify-center gap-2 shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>Continue purchase</span>
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>

          {/* Terms */}
          <p className="text-xs text-gray-500 text-center leading-relaxed">
            By purchasing Senalign tokens, you agree to our{" "}
            <a href="#" className="text-blue-600 hover:underline">
              Terms of Service
            </a>{" "}
            and our{" "}
            <a href="#" className="text-blue-600 hover:underline">
              Privacy Policy
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};
