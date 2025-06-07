import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";
import LoadingSpinner from "../components/LoadingSpinner";
import ProgressBar from "../components/ProgressBar";
//import GoogleMapView from "../components/GoogleMapView";
import PlaceDetailPage from "./PlaceDetail";
import KakaoMapView from "../components/KakaoMapView";

export default function TravelPlan() {
  const navigate = useNavigate();
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [aiEmpathy, setAiEmpathy] = useState("");
  const [tags, setTags] = useState([]);
  const [plans, setPlans] = useState([]);
  const [activeDay, setActiveDay] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [travelStyle, setTravelStyle] = useState(null);

  const VITE_API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  // const places = [
  //   {
  //     name: "경복궁",
  //     lat: 37.579617,
  //     lng: 126.977041,
  //     description: "조선의 정궁, 전통과 아름다움의 상징",
  //   },
  //   {
  //     name: "북촌한옥마을",
  //     lat: 37.582604,
  //     lng: 126.983998,
  //     description: "한옥의 고즈넉함과 인생샷 스팟!",
  //   },
  //   {
  //     name: "광장시장 육회골목",
  //     lat: 37.570376,
  //     lng: 126.999076,
  //     description: "서울 3대 육회, 광장시장 필수코스",
  //   },
  //   {
  //     name: "N서울타워",
  //     lat: 37.551169,
  //     lng: 126.988227,
  //     description: "서울 전경 한눈에, 야경 명소!",
  //   },
  //   {
  //     name: "카페 온더플레이트",
  //     lat: 37.545226,
  //     lng: 127.004885,
  //     description: "한강뷰 감성카페 ☕️🌉",
  //   },
  // ];

  useEffect(() => {
    async function fetchData() {
      setIsLoading(true);
      try {
        const stored = JSON.parse(localStorage.getItem("travelStyle"));

        if (!stored) {
          console.warn("로컬 스토리지에 사용자 성향 정보 없음");
          setIsLoading(false);
          return;
        }

        setTravelStyle(stored);

        const res = await axios.post(`${VITE_API_BASE_URL}/ai/schedule/`, {
          startCity: stored.startCity,
          endCity: stored.endCity,
          startDate: stored.startDate,
          endDate: stored.endDate,
          emotions: stored.emotions,
          companions: stored.companions,
          peopleCount: stored.peopleCount,
        });

        setStartDate(stored.startDate);
        setEndDate(stored.endDate);
        setTags(res.data.tags || []);
        setAiEmpathy(res.data.aiEmpathy || "AI 코멘트 없음");

        // 🔐 방어 코드
        if (Array.isArray(res.data.plans)) {
          setPlans(res.data.plans);
          localStorage.setItem("travelPlan", JSON.stringify({
            plans: res.data.plans,
            peopleCount: stored.peopleCount,
            endCity: stored.endCity,
          }));
        } else {
          console.warn("plans가 배열이 아닙니다:", res.data.plans);
          setPlans([]);
        }
        setIsLoading(false);
      } catch (err) {
        console.error("에러 발생", err);
        setIsLoading(false);
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
  }, []);

  if (isLoading)
    return (
      <>
        <Header />
        {/* <LoadingSpinner /> */}
        <ProgressBar />
      </>
    );

  return (
    <>
      <Header />
      <div className="max-w-5xl mx-auto p-6 bg-blue-50 min-h-screen text-blue-900">
        {/* 헤더 밑 윗줄 */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">여행 일정</h1>
          <p className="text-sm text-blue-600">
            📅 {startDate} ~ {endDate}
          </p>
          <div className="mt-2 space-x-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-block bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded-full"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>

        {/* AI 코멘트 */}
        <div className="flex items-start bg-blue-100 p-4 rounded-lg mb-6">
          <div className="mr-3 text-2xl">AI 코멘트</div>
          <p className="text-sm">
            {aiEmpathy || "로딩 중"}
          </p>
        </div>

        {/* Day Selector */}
        <div className="flex space-x-2 mb-4">
          {plans.map((plan) => (
            <button
              key={plan.day}
              onClick={() => setActiveDay(plan.day)}
              className={`px-4 py-2 rounded-lg font-medium border ${
                activeDay === plan.day
                  ? "bg-blue-700 text-white"
                  : "bg-white text-blue-700 border-blue-400"
              }`}
            >
              {" "}
              <span className="text-xs ml-1">Day: {plan.day}</span>
            </button>
          ))}
        </div>

        {/* Schedule */}
        {plans
          .find((plan) => plan.day === activeDay)
          ?.schedule?.map((item, idx) => (
            <div key={idx} className="bg-white p-4 rounded-lg shadow">
              <div className="flex items-center justify-between mb-2">
                <span className="text-blue-700 font-semibold">{item.time}</span>
                {/* <span className="bg-blue-100 text-blue-700 px-2 py-0.5 text-xs rounded">
                  {item.placeType}
                </span> */}
              </div>
              <h3 className="text-lg font-bold">{item.place}</h3>
              <p className="text-sm text-blue-700">{item.aiComment}</p>
              <div className="mt-2 flex space-x-2 text-xs">
                <button
                  className="bg-blue-200 text-blue-800 px-2 py-1 rounded"
                  onClick={() =>
                    navigate("/PlaceDetailPage", {
                      state: {
                        placeId: item.placeId,
                        emotions: travelStyle?.emotions,
                        companions: travelStyle?.companions,
                        peopleCount: travelStyle?.peopleCount,
                       },
                    })
                  }
                >
                  상세정보
                </button>
                <button className="bg-blue-200 text-blue-800 px-2 py-1 rounded">
                  수정
                </button>
              </div>
            </div>
          ))}

        <div className="google-map">
          <h2 className="text-xl font-semibold mb-2">동선 추천</h2>
          <KakaoMapView
            places={
              plans
                .find((plan) => plan.day === activeDay)
                ?.schedule?.map((item) => ({
                  name: item.place,
                  lat: item.latitude,
                  lng: item.longitude,
                })) || []
            }
          />
        </div>

        {/* Bottom Buttons */}
        <div className="flex flex-wrap gap-2 mt-10">
          {/* <button className="flex items-center gap-2 bg-blue-700 text-white px-4 py-2 rounded-lg">
            🔄 다시 추천받기
          </button> */}
          {/* <button className="bg-blue-500 text-white px-4 py-2 rounded-lg">
            + 내 일정으로 담기
          </button> */}
          <button
            onClick={() => navigate("/MyPlan")}
            className="bg-white text-blue-700 border border-blue-400 px-4 py-2 rounded-lg"
          >
            저장한 일정 보기
          </button>
          <button
            onClick={() => navigate("/TravelStyleForm")}
            className="bg-white text-blue-700 border border-blue-400 px-4 py-2 rounded-lg"
          >
            성향 입력 다시하기
          </button>
          <button
            onClick={() => navigate("/Budget")}
            className="bg-white text-blue-700 border border-blue-400 px-4 py-2 rounded-lg"
          >
            여행 예산 확인하기
          </button>
          {/* <button className="bg-white text-blue-700 border border-blue-400 px-4 py-2 rounded-lg">친구와 공유하기 (시간 남으면 구현)</button> */}
        </div>
      </div>
      <Footer />
    </>
  );
}