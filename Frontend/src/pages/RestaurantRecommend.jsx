import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import GoogleMapView from "../components/GoogleMapView";

export default function RestaurantRecommendationPage() {
  const navigate = useNavigate();

  return (
    <>
      <Header />

      <div className="min-h-screen bg-gradient-to-b from-blue-100 to-blue-300 p-4">
        <div className="text-xl text-blue-800 font-medium">맛집 리스트</div>

        {/* AI 추천 카드 */}
        <div className="bg-white shadow-md rounded-xl p-4 mb-6">
          <div className="text-sm text-blue-800 font-medium">
            거기 어때 AI의 추천!
          </div>
          <p className="text-blue-700 mt-1">
            해산물 좋아하신다면 해운대 "청초횟집"을 추천드려요. 현지인 리뷰가
            좋고, 가성비도 뛰어나요.
          </p>
        </div>

        {/* 추천 맛집 카드 */}
        <div className="bg-white shadow-md rounded-xl p-4 mb-6">
          <div className="flex gap-4">
            <div className="bg-blue-100 w-32 h-32 flex items-center justify-center text-blue-400 rounded-lg">
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

              <div className="mt-3 flex items-center gap-2 flex-wrap">
                <span className="text-sm text-blue-700 bg-blue-100 px-3 py-1 rounded-lg">
                  2만원대
                </span>
                <button
                  onClick={() => navigate("/RestaurantDetail")}
                  className="bg-blue-600 text-white text-sm px-3 py-1 rounded-lg hover:bg-blue-700"
                >
                  상세보기
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 지도 영역 */}
        <GoogleMapView />
      </div>
    </>
  );
}
