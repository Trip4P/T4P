import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import LoadingSpinner from "../../components/LoadingSpinner";
import KakaoMapView from "../../components/KakaoMapView";

export default function RestaurantDetailPage() {
  const location = useLocation();
  const { placeId, companions, foodPreferences, atmospheres } =
    location.state || {};
  const [placeData, setPlaceData] = useState(null);

  const VITE_API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  useEffect(() => {
    if (placeId) {
      axios
        .post(`${VITE_API_BASE_URL}/api/food-places-detail`, {
          placeId: placeId,
          companions: companions || [],
          atmospheres: atmospheres || [],
        })
        .then((res) => {
          // 응답이 HTML이면 잘못된 응답 처리
          if (
            typeof res.data === "string" &&
            res.data.includes("<!doctype html>")
          ) {
            console.error(
              "잘못된 API 응답입니다. 해당 API가 없을 수 있습니다."
            );
            setPlaceData(null);
          } else {
            setPlaceData(res.data);
          }
        })
        .catch((err) => {
          console.error("API 호출 실패:", err);
          setPlaceData(null);
        });
    }
  }, [placeId]);

  if (!placeData)
    return (
      <>
        <Header />
        <LoadingSpinner />
      </>
    );

  return (
    <>
      <Header />
      <div className="bg-white text-gray-800">
        <div className="w-full h-64 flex items-center justify-center">
          <div className="w-full flex justify-center">
            <div
              className="w-[900px] h-64 bg-center bg-cover"
              style={{
                backgroundImage: placeData.image
                  ? `url(${placeData.image})`
                  : "none",
                backgroundColor: placeData.image ? "transparent" : "#3B82F6",
              }}
            >
              {!placeData.image && (
                <span className="text-white font-bold text-xl flex items-center justify-center h-full">
                  이미지
                </span>
              )}
            </div>
          </div>
        </div>

        {/* 가게 정보 */}
        <div className="max-w-4xl mx-auto p-6">
          <h1 className="text-3xl font-bold text-blue-800 mb-2">
            {placeData.place}
          </h1>
          <div className="flex gap-2 mb-4">
            {placeData.tags.map((tag, i) => (
              <span
                key={i}
                className="bg-blue-100 text-blue-600 px-2 py-1 rounded text-sm"
              >
                {tag}
              </span>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm text-gray-700 mb-6">
            <div>
              <p className="font-semibold">영업시간</p>
              <p style={{ whiteSpace: "pre-line" }}>
                {placeData.businessHours}
              </p>
            </div>
            <div>
              <p className="font-semibold">가격대</p>
              <p>{placeData.price}</p>
            </div>
            <div>
              <p className="font-semibold">주소</p>
              <p>{placeData.address}</p>
            </div>
            <div>
              <p className="font-semibold">전화 번호</p>
              <p>{placeData.phone}</p>
            </div>
            <div>
              <p className="font-semibold">평균 평점</p>
              <p>
                {placeData.averageRate} ({placeData.reviewCount}개 리뷰)
              </p>
            </div>
          </div>

          {/* AI 추천 포인트 */}
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <h2 className="text-blue-700 font-semibold mb-2">AI 추천 포인트</h2>
            <p>{placeData.aiComment}</p>
          </div>

          {/* 리뷰 하이라이트 */}
          <div className="mb-6">
            <h2 className="text-blue-700 font-semibold mb-4">
              리뷰 하이라이트
            </h2>
            <div className="flex items-start gap-4 mb-2">
              <div>
                <p className="font-semibold">
                  {placeData.reviewHighlights.title}
                </p>
                <p className="text-sm text-gray-500 mb-1">
                  {placeData.reviewHighlights.date}
                </p>
                <p>{placeData.reviewHighlights.review}</p>
              </div>
            </div>
            <div className="mt-2">
              <p className="text-sm mb-1">
                만족도{" "}
                <span className="font-semibold">{placeData.satisfaction}%</span>
              </p>
              <div className="w-full h-2 bg-gray-200 rounded-full">
                <div className="w-[87%] h-full bg-blue-500 rounded-full" />
              </div>
            </div>
            <div className="mt-3 flex gap-2 flex-wrap text-sm">
              {placeData.reviewKeywords.map((tag, i) => (
                <span
                  key={i}
                  className="bg-blue-100 text-blue-600 px-2 py-1 rounded"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </div>

          {/* 위치 정보 */}
          <div className="bg-gray-100 rounded-lg p-4">
            <h2 className="text-blue-700 font-semibold mb-2">위치 정보</h2>
            <KakaoMapView
              places={
                placeData.latitude && placeData.longitude
                  ? [
                      {
                        lat: parseFloat(placeData.latitude),
                        lng: parseFloat(placeData.longitude),
                        name: placeData.place,
                      },
                    ]
                  : []
              }
            />
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
}