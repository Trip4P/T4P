import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";
import LoadingSpinner from "../components/LoadingSpinner";
import GoogleMapView from "../components/GoogleMapView";

export default function RestaurantRecommendationPage() {
  const navigate = useNavigate();
  const [places, setPlaces] = useState([]);
  const [aiComment, setAiComment] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const tasteProfile = JSON.parse(localStorage.getItem("tasteProfile")); // 로컬스토리지에 저장된 맛집 성향 가져오기

    if (tasteProfile) {
      setIsLoading(true);
      axios
        .post("http://127.0.0.1:8000/ai/restaurant", {
          companion: tasteProfile.companions,
          foodPreference: tasteProfile.foodPreference,
          atmospheres: tasteProfile.atmospheres,
          city: tasteProfile.city,
          region: tasteProfile.region,
        })
        .then((res) => {
          setAiComment(res.data.aiComment);
          setPlaces(res.data.places);
          setIsLoading(false);
        })
        .catch((err) => {
          console.error("맛집 추천 API 호출 실패", err);
          setIsLoading(false);
        });
    }
  }, []);

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

  if (isLoading)
    return (
      <>
        <Header />
        <LoadingSpinner />
      </>
    );

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
          {/* <p className="text-blue-700 mt-1">
            해산물 좋아하신다면 해운대 "청초횟집"을 추천드려요. 현지인 리뷰가
            좋고, 가성비도 뛰어나요.
          </p> */}
          <p className="text-blue-700 mt-1">{aiComment}</p>
        </div>

        {/* 추천 맛집 카드 */}
        {/* 로컬에서 레이아웃 어떻게 나오는지 확인용 */}
        {/* <div className="bg-white shadow-md rounded-xl p-4 mb-6">
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
        </div> */}

        {/* api 응답값 뿌려주기 */}
        {places.map((place, index) => (
          <div key={index} className="bg-white shadow-md rounded-xl p-4 mb-6">
            <div className="flex gap-4">
              <div className="bg-blue-100 w-32 h-32 flex items-center justify-center text-blue-400 rounded-lg">
                음식 이미지
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-blue-900">
                  {place.name}
                </h2>
                <div className="mt-1 space-x-2">
                  {place.tags &&
                    place.tags.map((tag, i) => (
                      <span
                        key={i}
                        className="bg-blue-200 text-blue-900 px-2 py-1 rounded-full text-xs"
                      >
                        #{tag}
                      </span>
                    ))}
                </div>
                <p className="text-sm text-blue-700 mt-2">
                  {place.aiFoodComment}
                </p>
                <div className="mt-3 flex items-center gap-2 flex-wrap">
                  <button
                    onClick={() =>
                      navigate("/RestaurantDetail", {
                        state: { placeId: place.placeId },
                      })
                    }
                    className="bg-blue-600 text-white text-sm px-3 py-1 rounded-lg hover:bg-blue-700"
                  >
                    상세보기
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* 지도 영역 */}
        {/* <GoogleMapView places={places} /> */}

        {/* Bottom Buttons */}
        <div className="flex flex-wrap gap-2 mt-10">
          <button className="flex items-center gap-2 bg-blue-700 text-white px-4 py-2 rounded-lg">
            🔄 다시 추천받기
          </button>
          <button
            onClick={() => navigate("/TravelStyleForm")}
            className="bg-white text-blue-700 border border-blue-400 px-4 py-2 rounded-lg"
          >
            성향 입력 다시하기
          </button>
          {/* <button className="bg-white text-blue-700 border border-blue-400 px-4 py-2 rounded-lg">친구와 공유하기 (시간 남으면 구현)</button> */}
        </div>
      </div>
      <Footer />
    </>
  );
}
