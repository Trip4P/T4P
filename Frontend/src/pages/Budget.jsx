// 여행 일정 추천하고 자동으로 예산 짜주는 페이지 (시나리오A)
import { Doughnut } from "react-chartjs-2";
import axios from "axios";
import { useEffect, useState } from "react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import Header from "../components/Header";
import LoadingSpinner from "../components/LoadingSpinner";
import Footer from "../components/Footer";

ChartJS.register(ArcElement, Tooltip, Legend);

const BudgetResultPage = () => {
  // Dummy data for chart (to be replaced with backend data)
  const [endCity, setEndCity] = useState("");
  const [dateRange, setDateRange] = useState("");
  const [totalBudget, setTotalBudget] = useState(0);
  const [categoryBreakdown, setCategoryBreakdown] = useState([]);
  const [aiComment, setAiComment] = useState("");
  const [peopleCount, setPeopleCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedStyle = JSON.parse(localStorage.getItem("travelStyle"));
    if (storedStyle) {
      setEndCity(storedStyle.endCity || "");
      setDateRange(`${storedStyle.startDate} ~ ${storedStyle.endDate}`);
    }

    const travelPlan = JSON.parse(localStorage.getItem("travelPlan"));
    console.log("travelPlan: " + travelPlan);
    if (travelPlan) {
      // endCity 추가
      if (storedStyle && storedStyle.endCity) {
        travelPlan.endCity = storedStyle.endCity;
      }

      if (travelPlan.peopleCount) {
        setPeopleCount(travelPlan.peopleCount);
      }
      axios
        .post("http://127.0.0.1:8000/api/schedules/budgets", travelPlan)
        .then((res) => {
          setTotalBudget(res.data.totalBudget);
          setCategoryBreakdown(res.data.categoryBreakdown);
          setAiComment(res.data.aiComment);
          setIsLoading(false);
        })
        .catch((err) => {
          console.error("예산 요청 실패", err)
          setIsLoading(false);
        });
    }
  }, []);

  if (isLoading) return (
    <>
      <Header />
      <LoadingSpinner />
    </>
  )

  const chartLabels = categoryBreakdown.map((item) => Object.keys(item)[0]);
  const chartData = categoryBreakdown.map((item) => Object.values(item)[0]);

  const data = {
    // labels: ["숙소", "교통", "식비", "기타"],
    labels: chartLabels,
    datasets: [
      {
        label: "비용 비중",
        // data: [300000, 150000, 180000, 90000],
        data: chartData,
        backgroundColor: [
          "#3B82F6", // blue-500
          "#60A5FA", // blue-400
          "#93C5FD", // blue-300
          "#BFDBFE", // blue-200
        ],
        borderWidth: 1,
      },
    ],
  };

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
              <div className="w-64 mx-auto md:mx-0">
                <Doughnut data={data} />
                {/* 테스트 코드용 */}
                <ul className="mt-4 text-sm text-center md:text-left">
                  {categoryBreakdown.map((item, idx) => {
                    const label = Object.keys(item)[0];
                    const value = Object.values(item)[0];
                    return (
                      <li key={idx}>
                        {label}: ₩ {value.toLocaleString()}
                      </li>
                    );
                  })}
                </ul>
              </div>
            </div>
          </section>

          {/* 설명 & 버튼 */}
          <section className="text-center space-y-4">
            {/* <p className="text-sm text-blue-600">
              예산 한줄평: 여행지 물가 기준으로는 꽤 여유로운 편이에요. 원하는
              곳 마음껏 즐기세요!
            </p> */}
            <p className="text-sm text-blue-600">{aiComment}</p>
            <div className="space-x-4">
              <button className="bg-white border border-blue-500 text-blue-600 rounded-lg px-4 py-2 hover:bg-blue-100 transition">
                예산 다시 추천 받기
              </button>
              <button className="bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 transition">
                예산 저장하고 일정 보기
              </button>
            </div>
          </section>
        </div>

        {/* Footer */}
        <footer className="text-center text-sm text-gray-400 mt-16">
          T4P &nbsp;|&nbsp; SPC 팀프로젝트 &nbsp;|&nbsp; 앗호
        </footer>
      </div>
      <Footer/>
    </>
  );
};

export default BudgetResultPage;