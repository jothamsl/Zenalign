import { CheckCircle } from "lucide-react";
import { useEffect } from "react";

export const PaymentSuccess = () => {
    useEffect(() => {
        // Optional: Auto-close after a few seconds
        // const timer = setTimeout(() => {
        //   window.close();
        // }, 5000);
        // return () => clearTimeout(timer);
    }, []);

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center space-y-6 animate-in fade-in zoom-in duration-300">
                <div className="mx-auto w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-10 h-10 text-green-600" />
                </div>

                <div className="space-y-2">
                    <h1 className="text-2xl font-bold text-gray-900">Payment Completed!</h1>
                    <p className="text-gray-500">
                        Your transaction has been processed successfully.
                    </p>
                </div>

                <div className="bg-blue-50 text-blue-700 p-4 rounded-xl text-sm">
                    Please close this window to return to the application and see your updated balance.
                </div>

                <button
                    onClick={() => window.close()}
                    className="w-full bg-gray-900 hover:bg-gray-800 text-white py-3 rounded-xl transition-colors font-medium"
                >
                    Close Window
                </button>
            </div>
        </div>
    );
};
