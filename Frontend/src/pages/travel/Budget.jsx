// 여행 일정 추천하고 자동으로 예산 짜주는 페이지 (시나리오A)
import { Doughnut } from "react-chartjs-2";
import axios from "axios";
import { useEffect, useState } from "react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import Header from "../../components/Header";
import LoadingSpinner from "../../components/LoadingSpinner";
import Footer from "../../components/Footer";
import Chart from "../../components/Chart";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function BudgetResultPage() {
  // Dummy data for chart (to be replaced with backend data)
  const [endCity, setEndCity] = useState("");
  const [dateRange, setDateRange] = useState("");
  const [totalBudget, setTotalBudget] = useState(0);
  const [categoryBreakdown, setCategoryBreakdown] = useState([]);
  const [aiComment, setAiComment] = useState("");
  const [peopleCount, setPeopleCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  const VITE_API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const fetchBudgetData = () => {
    const storedStyle = JSON.parse(localStorage.getItem("travelStyle"));
    const travelPlan = JSON.parse(localStorage.getItem("travelPlan"));

    if (storedStyle && storedStyle.endCity) {
      travelPlan.endCity = storedStyle.endCity;
    }

    if (travelPlan.peopleCount) {
      setPeopleCount(travelPlan.peopleCount);
    }

    setEndCity(storedStyle?.endCity || "");
    setDateRange(`${storedStyle?.startDate} ~ ${storedStyle?.endDate}`);
    setIsLoading(true);

    axios
      .post(`${VITE_API_BASE_URL}/api/schedules/budgets`, travelPlan)
      .then((res) => {
        setTotalBudget(res.data.totalBudget);
        setCategoryBreakdown(res.data.categoryBreakdown);
        setAiComment(res.data.aiComment);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("예산 요청 실패", err);
        setIsLoading(false);
      });
  };

  useEffect(() => {
    fetchBudgetData();
  }, []);

  if (isLoading) return (
    <>
      <Header />
      <LoadingSpinner />
    </>
  )

  return (
    <>
      <Header />
      <div className="bg-blue-50 min-h-screen py-16 px-6">
        <h1 className="text-2xl font-bold text-center text-blue-800 mb-12">
          예상 여행 예산을 알려드립니다
        </h1>

        <div className="max-w-4xl mx-auto bg-white shadow-md rounded-xl p-8 space-y-12">
          {/* 여행 정보 요약 */}
          <section>
            <h2 className="text-xl font-semibold text-blue-700 mb-6">
              여행 정보 요약
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-100 rounded-lg p-4">
                <p className="text-gray-600">목적지</p>
                <p className="font-semibold">{endCity}</p>
              </div>
              <div className="bg-blue-100 rounded-lg p-4">
                <p className="text-gray-600">여행일</p>
                <p className="font-semibold">{dateRange}</p>
              </div>
              <div className="bg-blue-100 rounded-lg p-4">
                <p className="text-gray-600">인원</p>
                <p className="font-semibold">{peopleCount}명</p>
              </div>
            </div>
          </section>

          {/* 예산 요약 */}
          <section>
            <h2 className="text-xl font-semibold text-blue-700 mb-6">
              예산 요약
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
              <div className="text-center md:text-left">
                <p className="text-gray-500 mb-2">총 예상 예산</p>
                {/* <p className="text-3xl font-bold text-blue-800">₩ 720,000</p> */}
                <p className="text-3xl font-bold text-blue-800">
                  ₩ {totalBudget.toLocaleString()}
                </p>
              </div>
            <Chart categoryBreakdown={categoryBreakdown} totalBudget={totalBudget} />
            </div>
          </section>

          {/* 설명 & 버튼 */}
          <section className="text-center space-y-4">
            <p className="text-sm text-blue-600">{aiComment}</p>
            <div className="space-x-4">
              <button
                onClick={fetchBudgetData}
                className="bg-white border border-blue-500 text-blue-600 rounded-lg px-4 py-2 hover:bg-blue-100 transition"
              >
                예산 다시 추천 받기
              </button>
              {/* <button className="bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 transition">
                예산 저장하고 일정 보기
              </button> */}
            </div>
          </section>
        </div>

      </div>
      <Footer/>
    </>
  );
};