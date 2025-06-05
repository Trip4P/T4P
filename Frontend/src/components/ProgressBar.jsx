import { useEffect, useState } from "react";

export default function ProgressBar({done = false}) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (done) {
      setProgress(100);
      return;
    }

    const interval = setInterval(() => {
      setProgress((prev) => (prev >= 90 ? prev : prev + Math.random() * 10));
    }, 500);
    return () => clearInterval(interval);
  }, [done]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4">
      <div className="w-full max-w-md bg-blue-100 rounded-full h-4 overflow-hidden mb-4">
        <div
          className="bg-blue-500 h-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <p className="text-blue-700">{done ? "완료!" : `로딩 중... ${Math.round(progress)}%`}</p>
    </div>
  )
}