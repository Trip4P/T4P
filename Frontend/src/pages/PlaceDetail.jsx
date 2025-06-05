// 여행 일정 추천 페이지에서 상세 정보를 눌렀을 때 나오는 페이지
import Header from "../components/Header";
import Footer from "../components/Footer";
import { useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";

export default function PlaceDetailPage() {
  const { state } = useLocation();
  const { placeId, emotions, companions, peopleCount } = state || {};
  const [placeData, setPlaceData] = useState(null);

  const VITE_API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  useEffect(() => {
    async function fetchPlaceDetail() {
      try {
        const response = await axios.post(`${VITE_API_BASE_URL}/api/place-detail`, {
          placeId: placeId,
          emotions: emotions,
          companions: companions,
          peopleCount: peopleCount
        });
        setPlaceData(response.data);
      } catch (error) {
        console.error("Failed to fetch place detail:", error);
      }
    }
    fetchPlaceDetail();
  }, [placeId]);

  if (!placeData) {
    return (
      <>
        <Header />
        <div className="p-6 text-center text-gray-600">Loading...</div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="bg-white text-gray-800">
        {/* 헤더 이미지 */}
        <div className="w-full h-64 bg-gradient-to-b from-blue-400 to-blue-600 flex items-center justify-center">
          <div className="w-24 h-24 bg-white rounded-md flex items-center justify-center overflow-hidden">
            {placeData.image ? (
              <img src={placeData.image} alt={placeData.place} className="object-cover w-full h-full" />
            ) : (
              <span className="text-blue-600 font-bold text-xl">이미지</span>
            )}
          </div>
        </div>

        {/* 가게 정보 */}
        <div className="max-w-4xl mx-auto p-6">
          <h1 className="text-3xl font-bold text-blue-800 mb-2">{placeData.place}</h1>
          <div className="flex gap-2 mb-4">
            {placeData.tags?.map((tag, idx) => (
              <span key={idx} className="bg-blue-100 text-blue-600 px-2 py-1 rounded text-sm">
                {tag}
              </span>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm text-gray-700 mb-6">
            {placeData.placeType !== "destination" && (
              <>
                <div>
                  <p className="font-semibold">영업시간</p>
                  <p>{placeData.businessHours}</p>
                </div>
                <div>
                  <p className="font-semibold">가격대</p>
                  <p>{placeData.price}</p>
                </div>
              </>
            )}
            <div>
              <p className="font-semibold">주소</p>
              <p>{placeData.address}</p>
            </div>
            {placeData.phone && (
              <div>
                <p className="font-semibold">전화번호</p>
                <p>{placeData.phone}</p>
              </div>
            )}
            {placeData.placeType !== "destination" && (
              <div>
                <p className="font-semibold">평균 평점</p>
                <p>
                  {placeData.averageRate} ({placeData.reviewCount}개 리뷰)
                </p>
              </div>
            )}
          </div>

          {/* AI 추천 포인트 */}
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <h2 className="text-blue-700 font-semibold mb-2">AI 추천 포인트</h2>
            <p>{placeData.aiComment}</p>
          </div>

          {/* 리뷰 하이라이트 */}
          <div className="mb-6">
            <h2 className="text-blue-700 font-semibold mb-4">리뷰 하이라이트</h2>
            <div className="flex items-start gap-4 mb-2">
              <div className="w-10 h-10 bg-gray-200 rounded-full" />
              <div>
                <p className="font-semibold">{placeData.reviewHighlights?.title}</p>
                <p className="text-sm text-gray-500 mb-1">{placeData.reviewHighlights?.date}</p>
                <p>{placeData.reviewHighlights?.review}</p>
              </div>
            </div>
            <div className="mt-2">
              <p className="text-sm mb-1">
                만족도 <span className="font-semibold">{placeData.satisfaction}%</span>
              </p>
              <div className="w-full h-2 bg-gray-200 rounded-full">
                <div
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${placeData.satisfaction}%` }}
                />
              </div>
            </div>
            <div className="mt-3 flex gap-2 flex-wrap text-sm">
              {placeData.reviewKeywords?.map((keyword, idx) => (
                <span key={idx} className="bg-blue-100 text-blue-600 px-2 py-1 rounded">
                  #{keyword}
                </span>
              ))}
            </div>
          </div>

          {/* 위치 정보 */}
          <div className="bg-gray-100 rounded-lg p-4">
            <h2 className="text-blue-700 font-semibold mb-2">위치 정보</h2>
            <div className="w-full h-60 bg-gray-300 rounded mb-4 flex items-center justify-center text-gray-500">
              지도 영역
            </div>
            <div className="flex gap-4">
              <button className="flex-1 py-2 px-4 bg-white border border-blue-500 text-blue-600 rounded hover:bg-blue-50">
                지도 보기
              </button>
              <button className="flex-1 py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600">
                길찾기 (구현할지 미정)
              </button>
            </div>
          </div>
        </div>
      </div>
      <Footer/>
    </>
  );
}
