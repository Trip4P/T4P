import React, { useState } from "react";
// import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import GoogleMapView from "../components/GoogleMapView";

export default function TravelPlan() {
  const navigate = useNavigate();
  const [activeDay, setActiveDay] = useState("DAY 1");

  const days = ["DAY 1", "DAY 2", "DAY 3"];

  const places = [
    {
      name: "경복궁",
      lat: 37.579617,
      lng: 126.977041,
      description: "조선의 정궁, 전통과 아름다움의 상징",
    },
    {
      name: "북촌한옥마을",
      lat: 37.582604,
      lng: 126.983998,
      description: "한옥의 고즈넉함과 인생샷 스팟!",
    },
    {
      name: "광장시장 육회골목",
      lat: 37.570376,
      lng: 126.999076,
      description: "서울 3대 육회, 광장시장 필수코스",
    },
    {
      name: "N서울타워",
      lat: 37.551169,
      lng: 126.988227,
      description: "서울 전경 한눈에, 야경 명소!",
    },
    {
      name: "카페 온더플레이트",
      lat: 37.545226,
      lng: 127.004885,
      description: "한강뷰 감성카페 ☕️🌉",
    },
  ];


  return (
    <>
      <Header />
      <div className="max-w-5xl mx-auto p-6 bg-blue-50 min-h-screen text-blue-900">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">부산 여행 일정</h1>
          <p className="text-sm text-blue-600">
            📅 2025.05.13 ~ 2025.05.15 (2박 3일)
          </p>
          <div className="mt-2 space-x-2">
            {["#미식", "#감성", "#바다", "#여유"].map((tag) => (
              <span
                key={tag}
                className="inline-block bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Tip Box */}
        <div className="flex items-start bg-blue-100 p-4 rounded-lg mb-6">
          <div className="mr-3 text-2xl">💡</div>
          <p className="text-sm">
            여유롭고 감성적인 여행을 원하셨죠? 감성 카페와 현지인 맛집 위주로
            구성했어요!
          </p>
        </div>

        {/* Day Selector */}
        <div className="flex space-x-2 mb-4">
          {days.map((day) => (
            <button
              key={day}
              onClick={() => setActiveDay(day)}
              className={`px-4 py-2 rounded-lg font-medium border ${
                activeDay === day
                  ? "bg-blue-700 text-white"
                  : "bg-white text-blue-700 border-blue-400"
              }`}
            >
              {day}{" "}
              <span className="text-xs ml-1">
                {day === "DAY 1"
                  ? "05.13"
                  : day === "DAY 2"
                  ? "05.14"
                  : "05.15"}
              </span>
            </button>
          ))}
        </div>

        {/* Schedule */}
        {activeDay === "DAY 1" && (
          <div className="space-y-6">
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="flex items-center justify-between mb-2">
                <span className="text-blue-700 font-semibold">09:00</span>
                <span className="bg-blue-100 text-blue-700 px-2 py-0.5 text-xs rounded">
                  체크인
                </span>
              </div>
              <h3 className="text-lg font-bold">호텔 부산</h3>
              <p className="text-sm text-blue-700">
                오션뷰 객실에서 여유로운 시작
              </p>
              <div className="mt-2 flex space-x-2 text-xs">
                <button className="bg-blue-200 text-blue-800 px-2 py-1 rounded">
                  상세정보
                </button>
                <button className="bg-blue-200 text-blue-800 px-2 py-1 rounded">
                  수정
                </button>
              </div>
            </div>

            <div className="bg-white p-4 rounded-lg shadow">
              <div className="flex items-center justify-between mb-2">
                <span className="text-blue-700 font-semibold">12:00</span>
                <span className="bg-blue-100 text-blue-700 px-2 py-0.5 text-xs rounded">
                  점심
                </span>
              </div>
              <h3 className="text-lg font-bold">청춘횟집</h3>
              <p className="text-sm text-blue-700">
                현지인이 추천하는 신선한 회와 물회
              </p>
              <div className="mt-2 space-x-2">
                {["#미식", "#현지맛집"].map((tag) => (
                  <span
                    key={tag}
                    className="inline-block bg-blue-200 text-blue-800 text-xs px-2 py-1 rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="google-map">
          <h2>동선 추천</h2>
          <GoogleMapView places={places} />
        </div>

        {/* Bottom Buttons */}
        <div className="flex flex-wrap gap-2 mt-10">
          <button className="flex items-center gap-2 bg-blue-700 text-white px-4 py-2 rounded-lg">
            🔄 다시 추천받기
          </button>
          <button className="bg-blue-500 text-white px-4 py-2 rounded-lg">
            + 내 일정으로 담기
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
    </>
  );
}
