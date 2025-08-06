import React, { useEffect, useState, useRef } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { CheckCircleIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";

const EmailVerificationPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { verifyEmail, resendVerification, loading } = useAuth();
  const [verifying, setVerifying] = useState(false);
  const [verified, setVerified] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const hasAttemptedVerification = useRef(false);
  const isVerifyingRef = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const token = searchParams.get("token");

  useEffect(() => {
    const handleVerification = async () => {
      // Prevent multiple concurrent verification attempts
      if (
        !token ||
        hasAttemptedVerification.current ||
        isVerifyingRef.current
      ) {
        return;
      }

      // Abort any previous requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller for this request
      abortControllerRef.current = new AbortController();

      hasAttemptedVerification.current = true;
      isVerifyingRef.current = true;
      setVerifying(true);
      setError(null);

      try {
        await verifyEmail(token);
        setVerified(true);
        setTimeout(() => {
          navigate("/dashboard");
        }, 2000);
      } catch (err) {
        // Don't show error if request was aborted
        if (!(err instanceof Error) || err.name !== "AbortError") {
          const errorMessage =
            err instanceof Error ? err.message : "Verification failed";

          // Handle rate limiting specifically
          if (errorMessage.includes("Too many")) {
            // Show a more user-friendly message for rate limiting
            setError(
              "Please wait a moment before trying again. If you continue to have issues, try refreshing the page."
            );
          } else {
            setError(errorMessage);
          }
        }
      } finally {
        setVerifying(false);
        isVerifyingRef.current = false;
      }
    };

    handleVerification();

    // Cleanup function to abort ongoing requests
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [token, verifyEmail, navigate]);

  const handleResendVerification = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      toast.error("Please enter your email address");
      return;
    }

    try {
      await resendVerification(email);
      setEmail("");
    } catch {
      // Error is already handled in context
    }
  };

  if (verifying) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <h2 className="mt-6 text-2xl font-bold text-gray-900">
              Verifying your email...
            </h2>
          </div>
        </div>
      </div>
    );
  }

  if (verified) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="text-center">
            <CheckCircleIcon className="mx-auto h-12 w-12 text-green-600" />
            <h2 className="mt-6 text-2xl font-bold text-gray-900">
              Email Verified Successfully!
            </h2>
            <p className="mt-2 text-gray-600">
              You are now logged in. Redirecting to dashboard...
            </p>
          </div>
        </div>
      </div>
    );
  }

  // If there's a token but verification failed
  if (token && error) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <div className="text-center">
              <div className="mx-auto h-12 w-12 text-red-600">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              <h2 className="mt-6 text-2xl font-bold text-gray-900">
                Verification Failed
              </h2>
              <p className="mt-2 text-red-600">{error}</p>

              <div className="mt-6">
                <form onSubmit={handleResendVerification} className="space-y-4">
                  <div>
                    <label
                      htmlFor="email"
                      className="block text-sm font-medium text-gray-700"
                    >
                      Resend verification email
                    </label>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      autoComplete="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Enter your email"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {loading ? "Sending..." : "Resend Verification"}
                  </button>
                </form>

                <div className="mt-4">
                  <Link
                    to="/login"
                    className="text-blue-600 hover:text-blue-500"
                  >
                    Back to Login
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Default case - show email verification instructions
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <CheckCircleIcon className="h-16 w-16 text-green-500" />
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Check your email
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          We've sent you a verification link
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Account Created Successfully!
            </h3>
            <p className="text-sm text-gray-600 mb-6">
              Please check your email and click the verification link to
              activate your account. Once verified, you'll be able to sign in
              and start using the Scientific Text Annotator.
            </p>

            <div className="space-y-4">
              <div className="text-xs text-gray-500">
                <p>• Check your spam/junk folder if you don't see the email</p>
                <p>• The verification link will expire in 24 hours</p>
                <p>
                  • You can close this page and return when you're ready to sign
                  in
                </p>
              </div>

              <div className="pt-4 border-t border-gray-200 space-y-2">
                <form onSubmit={handleResendVerification} className="space-y-4">
                  <div>
                    <label
                      htmlFor="resend-email"
                      className="block text-sm font-medium text-gray-700"
                    >
                      Didn't receive an email? Resend verification
                    </label>
                    <input
                      id="resend-email"
                      name="email"
                      type="email"
                      autoComplete="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Enter your email"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {loading ? "Sending..." : "Resend Verification"}
                  </button>
                </form>

                <Link
                  to="/login"
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Go to Sign In
                </Link>
                <Link
                  to="/"
                  className="block text-sm text-center text-primary-600 hover:text-primary-500"
                >
                  ← Back to Home
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationPage;
