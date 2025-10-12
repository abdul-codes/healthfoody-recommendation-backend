interface LoadingSpinnerProps {
  message?: string;
}

export function LoadingSpinner({ message = "Loading recommendations..." }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 space-y-6">
      {/* Animated food bubbles with better colors */}
      <div className="relative">
        <div className="flex space-x-3">
          <div className="w-6 h-6 bg-emerald-500 rounded-full animate-bounce shadow-lg" style={{animationDelay: '0ms'}}></div>
          <div className="w-6 h-6 bg-teal-500 rounded-full animate-bounce shadow-lg" style={{animationDelay: '150ms'}}></div>
          <div className="w-6 h-6 bg-green-500 rounded-full animate-bounce shadow-lg" style={{animationDelay: '300ms'}}></div>
          <div className="w-6 h-6 bg-lime-500 rounded-full animate-bounce shadow-lg" style={{animationDelay: '450ms'}}></div>
        </div>
      </div>
      
      {/* Elegant spinner */}
      <div className="relative">
        <div className="w-16 h-16 border-4 border-gray-200 rounded-full animate-spin">
          <div className="absolute top-0 left-0 w-16 h-16 border-4 border-emerald-500 rounded-full animate-spin border-t-transparent shadow-sm"></div>
        </div>
      </div>
      
      {/* Loading message */}
      <div className="text-center space-y-3">
        <p className="text-xl font-semibold text-gray-700">{message}</p>
        <div className="flex items-center justify-center space-x-1">
          <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
          <span className="w-2 h-2 bg-teal-500 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></span>
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></span>
        </div>
        <p className="text-sm text-gray-500 max-w-xs">
          Analyzing your condition with AI and fetching nutritional data
        </p>
      </div>
    </div>
  );
}
