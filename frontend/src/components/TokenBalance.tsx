import React, { useState, useEffect } from "react";
import { senalignAPI } from "../services/api";
import { Coins, AlertCircle, RefreshCw } from "lucide-react";

interface TokenBalanceProps {
  userEmail: string;
  onPurchaseClick?: () => void;
}

interface TokenBalanceData {
  user_email: string;
  token_balance: number;
  total_purchased: number;
  total_consumed: number;
  last_purchase_date?: string;
}

export const TokenBalance: React.FC<TokenBalanceProps> = ({
  userEmail,
  onPurchaseClick,
}) => {
  const [balance, setBalance] = useState<TokenBalanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBalance = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await senalignAPI.getTokenBalance(userEmail);
      setBalance(data);
    } catch (err: any) {
      console.error("Failed to fetch token balance:", err);
      setError(err.response?.data?.detail || "Failed to load balance");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userEmail) {
      fetchBalance();
    }
  }, [userEmail]);

  if (loading) {
    return (
      <div className="flex items-center space-x-2 text-gray-600">
        <RefreshCw className="w-4 h-4 animate-spin" />
        <span className="text-sm">Loading balance...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center space-x-2 text-red-600">
        <AlertCircle className="w-4 h-4" />
        <span className="text-sm">{error}</span>
      </div>
    );
  }

  if (!balance) {
    return null;
  }

  const isLowBalance = balance.token_balance < 20;

  return (
    <div className="flex items-center space-x-4">
      <div
        className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
          isLowBalance
            ? "bg-amber-50 border border-amber-200"
            : "bg-green-50 border border-green-200"
        }`}
      >
        <Coins
          className={`w-5 h-5 ${isLowBalance ? "text-amber-600" : "text-green-600"}`}
        />
        <div className="flex flex-col">
          <span
            className={`text-lg font-bold ${isLowBalance ? "text-amber-700" : "text-green-700"}`}
          >
            {balance.token_balance} tokens
          </span>
          <span className="text-xs text-gray-500">
            {balance.total_purchased} purchased • {balance.total_consumed}{" "}
            used
          </span>
        </div>
      </div>

      {isLowBalance && (
        <div className="flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-amber-600" />
          <span className="text-sm text-amber-700">Low balance</span>
        </div>
      )}

      <button
        onClick={onPurchaseClick}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
      >
        Buy Tokens
      </button>

      <button
        onClick={fetchBalance}
        className="p-2 text-gray-600 hover:text-gray-800 rounded-lg hover:bg-gray-100 transition-colors"
        title="Refresh balance"
      >
        <RefreshCw className="w-4 h-4" />
      </button>
    </div>
  );
};
