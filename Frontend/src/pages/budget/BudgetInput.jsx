// 사용자가 일정 추천 안 받고 여행 정보 입력하여 예산 뽑아주는 페이지 (시나리오 B)
import { useState } from "react";
import axios from "axios";
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import DatePicker from "react-datepicker";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import Chart from "../../components/Chart";
import LoadingSpinner from "../../components/LoadingSpinner";

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

const generateColors = (count) => {
  const colors = [];
  for (let i = 0; i < count; i++) {
    // hue 범위를 파랑 계열로 제한 (약 180 ~ 250)
    const hue = 180 + Math.floor(Math.random() * 70); // 180~250 사이 정수
    const saturation = 70 + Math.floor(Math.random() * 10); // 70~80%
    const lightness = 50 + Math.floor(Math.random() * 10); // 50~60%
    colors.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
  }
  return colors;
};

const formatDateKorean = (date) =>
  date
    ?.toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    })
    .replace(/\. /g, "-")
    .replace(/\./g, "");

export default function TravelBudgetInputPage() {
  const [showResult, setShowResult] = useState(false);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [startCity, setStartCtiy] = useState("");
  const [endCity, setEndCity] = useState("");
  const [peopleCount, setPeopleCount] = useState("");
  const [budgetData, setBudgetData] = useState(null);
  const [aiComment, setAiComment] = useState("");
  const [totalBudget, setTotalBudget] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const VITE_API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const fetchBudgetData = async () => {
    try {
      setIsLoading(true);
      setShowResult(false);
      const res = await axios.post(`${VITE_API_BASE_URL}/api/budgets`, {
        startCity,
        endCity,
        startDate: formatDateKorean(startDate),
        endDate: formatDateKorean(endDate),
        peopleNum: peopleCount,
      });

      const response = res.data;
      const entries = Object.entries(response.categoryBreakdown || {});
      const labels = entries.map(([key]) => key);
      const values = entries.map(([, value]) => value);
      const backgroundColors = generateColors(labels.length);

      setBudgetData({
        labels,
        datasets: [
          {
            label: "예상 예산 (원)",
            data: values,
            backgroundColor: backgroundColors,
            borderWidth: 1,
          },
        ],
      });

      setAiComment(response.aiComment);
      setShowResult(true);
      setTotalBudget(response.totalBudget);
    } catch (err) {
      console.error("API호출 실패", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Header />
      <div className="min-h-screen bg-gradient-to-b from-blue-100 to-white p-6">
        <h1 className="text-3xl font-bold text-center text-blue-900">
          여행 예산 입력하기
        </h1>
        <h1 className="text-center text-blue-700 mb-8">
          출발지, 도착지, 기간, 인원 수를 입력하고 예상 여행 예산을
          계산해보세요.
        </h1>

        <div className="max-w-3xl mx-auto">
          {/* 여행 정보 입력 */}
          <div className="bg-blue-50 p-6 rounded-xl shadow-md mb-6">
            <h1 className="text-xl font-semibold text-blue-700 mb-4">
              여행 정보 입력
            </h1>

            <div className="mb-4">
              <p className="text-sm text-blue-700 mb-1">출발지 입력</p>
              <input
                type="text"
                value={startCity}
                onChange={(e) => setStartCtiy(e.target.value)}
                placeholder="ex) 고속버스터미널"
                className="w-full border border-blue-300 rounded px-4 py-2"
              />
            </div>

            <div className="mb-4">
              <p className="text-sm text-blue-700 mb-1">도착지 입력</p>
              <input
                type="text"
                value={endCity}
                onChange={(e) => setEndCity(e.target.value)}
                placeholder="ex) 잠실"
                className="w-full border border-blue-300 rounded px-4 py-2"
              />
            </div>

            <div className="mb-4">
              <p className="text-sm text-blue-700 mb-1">인원 수 선택</p>
              <input
                type="number"
                value={peopleCount}
                onChange={(e) => {
                  const value = e.target.value;
                  setPeopleCount(value === "" ? "" : Number(value));
                }}
                placeholder="ex) 3"
                className="w-full border border-blue-300 rounded px-4 py-2"
              />
            </div>

            <div className="bg-blue-50 rounded-xl p-6 mb-10">
              <h2 className="text-blue-700 text-lg font-semibold mb-4">
                여행 기간
              </h2>
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex flex-col">
                  <label className="text-blue-700 mb-1 font-medium">
                    여행 시작일
                  </label>
                  <DatePicker
                    selected={startDate}
                    onChange={(date) => setStartDate(date)}
                    selectStart
                    startDate={startDate}
                    endDate={endDate}
                    placeholderText="시작일 선택"
                    dateFormat="yyyy-MM-dd"
                    className="border border-blue-300 rounded px-4 py-2"
                  />
                </div>

                <div className="flex flex-col">
                  <label className="text-blue-700 mb-1 font-medium">
                    여행 종료일
                  </label>
                  <DatePicker
                    selected={endDate}
                    onChange={(date) => setEndDate(date)}
                    selectsEnd
                    startDate={startDate}
                    endDate={endDate}
                    placeholderText="종료일 선택"
                    dateFormat="yyyy-MM-dd"
                    className="border border-blue-300 rounded px-4 py-2"
                  />
                </div>
              </div>
            </div>

            {/* 버튼 */}
            <div className="text-center mt-6">
              <button
                onClick={fetchBudgetData}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                예상 예산 출력하기
              </button>
            </div>
          </div>

          {isLoading && <LoadingSpinner />}

          {/* 예상 예산 결과 박스 */}
          {showResult && budgetData && (
            <div className="bg-white mt-10 p-8 rounded-xl shadow-lg border border-gray-200">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-20 h-14 bg-blue-100 text-blue-700 flex items-center justify-center rounded-full font-bold text-lg">
                    <img
                      src="/businessman.png"
                      alt="ai 아이콘"
                      className="w-7 h-auto"
                    />
                  </div>
                  <p className="text-lg font-medium text-gray-800">
                    {aiComment}
                  </p>
                </div>
                <p className="text-xl font-bold text-gray-900">
                  총 예산: {totalBudget?.toLocaleString()}원
                </p>
              </div>
              <h3 className="text-lg font-semibold mb-4 text-gray-700 border-b pb-2 mt-5">
                카테고리별 예상 예산
              </h3>

              {/* 예산 차트 */}
              <div className="mt-10 flex justify-center">
                <Chart
                  categoryBreakdown={budgetData.labels.map((label, idx) => ({
                    [label]: budgetData.datasets[0].data[idx],
                  }))}
                  totalBudget={totalBudget}
                />
              </div>

              {/* 버튼들 */}
              <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  className="border border-gray-400 px-5 py-2.5 rounded-lg hover:bg-gray-100 transition font-medium text-gray-700"
                  onClick={fetchBudgetData}
                >
                  예산 다시 추천 받기
                </button>
                {/* <button className="bg-blue-700 text-white px-5 py-2.5 rounded-lg hover:bg-blue-800 transition font-medium">
                ✅ 예산 저장하고 일정 보기
                </button> */}
              </div>
            </div>
          )}
        </div>
      </div>
      <Footer />
    </>
  );
}