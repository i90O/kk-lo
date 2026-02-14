"use client";

export default function StrengthMeter({ strength, signal }: {
  strength: number;
  signal: string;
}) {
  const color = signal === "bullish" ? "bg-green-400" : signal === "bearish" ? "bg-red-400" : "bg-yellow-400";
  const dim = "bg-gray-700";
  return (
    <div className="flex gap-1 items-center">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className={`w-2 h-2 rounded-full ${i <= strength ? color : dim}`} />
      ))}
    </div>
  );
}
