import { useEffect, useState } from "react";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import KakaoMapView from "../../components/KakaoMapView";

export default function MyPlan() {
  const [savedPlan, setSavedPlan] = useState(null);
  const [plans, setPlans] = useState([]);
  const [activeDay, setActiveDay] = useState(1);

  useEffect(() => {
    const stored = localStorage.getItem("travelPlan");
    if (stored) {
      const parsed = JSON.parse(stored);
      setSavedPlan(parsed);
      setPlans(parsed.plans || []);
    }
  }, []);

  return (
    <>
      <Header />
      <div className="max-w-6xl mx-auto p-6 min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 text-blue-900 rounded-lg shadow-md">
        <h1 className="text-4xl font-extrabold mb-6 text-center text-blue-800">나의 저장된 여행 일정</h1>
        {savedPlan && savedPlan.plans ? (
          savedPlan.plans.map((plan) => (
            <div key={plan.day} className="mb-8">
              <h2 className="text-2xl font-bold text-blue-700 mb-3 border-b-2 border-blue-300 pb-1">Day {plan.day}</h2>
              {plan.schedule.map((item, idx) => (
                <div key={idx} className="bg-white p-4 rounded-lg border-l-4 border-blue-400 shadow-sm hover:shadow-md transition-shadow duration-300 mb-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-blue-600 font-semibold">{item.time}</span>
                    <span className="text-lg font-bold text-blue-800">{item.place}</span>
                  </div>
                  <p className="text-sm text-blue-600">{item.aiComment}</p>
                </div>
              ))}
            </div>
          ))
        ) : (
          <p className="text-gray-600 text-center text-lg">저장된 일정이 없습니다.</p>
        )}

        <div className="mt-12">
          <h2 className="text-2xl font-bold text-blue-700 mb-3 border-b-2 border-blue-300 pb-1">📍 여행 동선</h2>
          <KakaoMapView
            places={plans.flatMap((plan) =>
              plan.schedule.map((item) => ({
                name: item.place,
                lat: item.latitude,
                lng: item.longitude,
              }))
            )}
          />
        </div>
      </div>
      <Footer />
    </>
  );
}
