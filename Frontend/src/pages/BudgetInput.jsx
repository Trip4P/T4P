import { useState } from "react";
import { Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import Header from "../components/Header";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function TravelBudgetInputPage() {
  const [showResult, setShowResult] = useState(false);

  // 💰 더미 예산 데이터
  const dummyBudgetData = {
    labels: ["항공", "숙박", "식비", "교통", "기타"],
    datasets: [
      {
        label: "예상 예산 (원)",
        data: [300000, 500000, 200000, 100000, 50000],
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
        ],
        borderWidth: 1,
      },
    ],
  };

  // 옵션 (툴팁 포맷 등)
  const chartOptions = {
    plugins: {
      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.label}: ${context.raw.toLocaleString()}원`;
          },
        },
      },
      legend: {
        position: "bottom",
      },
    },
  };

  return (
    <>
      <Header />
      <div className="p-6 max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-blue-700">
          여행 예산 입력하기
        </h1>
        <p className="text-center text-gray-600 mt-2">
          목적지, 기간, 인원 수를 입력하고 예상 여행 예산을 계산해보세요.
        </p>

        {/* 여행 정보 입력 */}
        <div className="bg-white p-6 rounded-lg shadow-md mt-8">
          <h2 className="text-xl font-semibold text-blue-700 mb-4">
            여행 정보 입력
          </h2>

          {/* 목적지 선택 */}
          <div className="mb-4">
            <p className="text-sm text-gray-700 mb-1">
              목적지 선택{" "}
              <span className="text-red-500">
                (예시입니다. 실제로는 더 많을 예정)
              </span>
            </p>
            <div className="flex flex-wrap gap-2">
              {["강원", "경남", "식사", "익선동", "경북궁"].map((region) => (
                <button
                  key={region}
                  className="px-4 py-2 rounded-lg bg-blue-100 text-blue-700 hover:bg-blue-200"
                >
                  {region}
                </button>
              ))}
            </div>
          </div>

          {/* 인원 수 선택 */}
          <div className="mb-4">
            <p className="text-sm text-gray-700 mb-1">인원 수 선택</p>
            <div className="flex flex-wrap gap-2">
              {["1명", "2명", "3명", "4명", "5명 이상"].map((n) => (
                <button
                  key={n}
                  className="px-4 py-2 rounded-lg bg-blue-100 text-blue-700 hover:bg-blue-200"
                >
                  {n}
                </button>
              ))}
            </div>
          </div>

          {/* 여행 기간 */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700">
              여행 기간 (출발일 ~ 도착일)
            </label>
            <input
              type="date"
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          {/* 버튼 */}
          <div className="text-center mt-6">
            <button
              onClick={() => setShowResult(true)}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              예상 예산 출력하기
            </button>
          </div>
        </div>

        {/* ✅ 예상 예산 결과 박스 */}
        {showResult && (
          <div className="bg-gray-100 mt-10 p-6 rounded-lg shadow-md">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gray-300 rounded-full" />
              <p className="text-lg font-semibold text-gray-800">
                예산 한줄평: 여행지 물가 기준으로는 꽤 여유로운 편이에요. 원하는
                곳 마음껏 즐기세요!
              </p>
            </div>

            {/* 📊 예산 차트 */}
            <div className="mt-8">
              <h3 className="text-md font-semibold mb-2 text-gray-700">
                카테고리별 예상 예산
              </h3>
              <Doughnut data={dummyBudgetData} options={chartOptions} />
            </div>

            {/* 버튼들 */}
            <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-end">
              <button className="border border-gray-600 px-4 py-2 rounded hover:bg-gray-200">
                예산 다시 추천 받기
              </button>
              <button className="bg-black text-white px-4 py-2 rounded hover:bg-gray-900">
                예산 저장하고 일정 보기
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
