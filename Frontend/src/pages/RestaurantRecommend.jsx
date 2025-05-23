import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";

export default function RestaurantRecommendationPage() {
  const navigate = useNavigate();

  return (
    <>
      <Header />
      <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-300 p-4">
        <header className="flex justify-between items-center mb-6">
          {/* <button className="text-blue-700 font-semibold">← 일정으로 돌아가기</button> */}
          <h1 className="text-blue-900 text-lg font-bold">Day 2 / 점심 추천</h1>
          {/* <span className="text-blue-700 text-sm">2025.05.13 / 12:30 PM</span> */}
        </header>

        {/* AI 추천 카드 */}
        <div className="bg-white shadow-md rounded-xl p-4 mb-6">
          <div className="text-sm text-blue-800 font-medium">
            TripMate AI의 추천!
          </div>
          <p className="text-blue-700 mt-1">
            해산물 좋아하신다면 해운대 "청초횟집"을 추천드려요. 현지인 리뷰가
            좋고, 가성비도 뛰어나요.
          </p>
        </div>

        {/* 추천 맛집 카드 */}
        <div className="bg-white shadow-md rounded-xl p-4 mb-6">
          <div className="flex gap-4">
            <div className="bg-blue-100 w-32 h-32 flex items-center justify-center text-blue-400">
              음식 이미지
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-blue-900">
                청초횟집{" "}
                <span className="text-sm font-medium">★ 4.7 (1,243)</span>
              </h2>
              <div className="mt-1 space-x-2">
                <span className="bg-blue-200 text-blue-900 px-2 py-1 rounded-full text-xs">
                  #가성비
                </span>
                <span className="bg-blue-200 text-blue-900 px-2 py-1 rounded-full text-xs">
                  #현지인맛집
                </span>
                <span className="bg-blue-200 text-blue-900 px-2 py-1 rounded-full text-xs">
                  #바다뷰
                </span>
              </div>
              <p className="text-sm text-blue-700 mt-2">
                신선한 해산물과 함께 즐기는 오션뷰. 현지인들에게 인기 있는
                맛집입니다.
              </p>
              <div className="mt-3 space-x-2">
                <button
                  onClick={() => navigate("/HotPlaceDetail")}
                  className="bg-blue-600 text-white text-sm px-3 py-1 rounded-lg hover:bg-blue-700"
                >
                  상세보기
                </button>
                <button className="bg-blue-100 text-blue-700 text-sm px-3 py-1 rounded-lg hover:bg-blue-200">
                  일정에 추가
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 거리 / 가격대 필터 */}
        <div className="bg-white shadow-md rounded-xl p-4 mb-6">
          <div className="mb-4">
            <p className="font-medium text-blue-800">거리</p>
            <div className="flex gap-2 mt-2">
              <button className="bg-blue-100 text-blue-700 px-3 py-1 rounded-lg hover:bg-blue-200">
                1km 이내
              </button>
              <button className="bg-blue-100 text-blue-700 px-3 py-1 rounded-lg hover:bg-blue-200">
                3km
              </button>
              <button className="bg-blue-100 text-blue-700 px-3 py-1 rounded-lg hover:bg-blue-200">
                전체
              </button>
            </div>
          </div>
          <div>
            <p className="font-medium text-blue-800">가격대</p>
            <div className="flex gap-2 mt-2">
              <button className="bg-blue-100 text-blue-700 px-3 py-1 rounded-lg hover:bg-blue-200">
                ₩
              </button>
              <button className="bg-blue-100 text-blue-700 px-3 py-1 rounded-lg hover:bg-blue-200">
                ₩₩
              </button>
              <button className="bg-blue-100 text-blue-700 px-3 py-1 rounded-lg hover:bg-blue-200">
                ₩₩₩
              </button>
            </div>
          </div>
        </div>

        {/* 지도 영역 */}
        <div className="bg-blue-100 rounded-xl h-64 flex items-center justify-center text-blue-400">
          지도 영역
        </div>
      </div>
    </>
  );
}
