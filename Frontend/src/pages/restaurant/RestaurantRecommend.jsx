import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import LottieAnimation from "../../components/LottieAnimation";

export default function RestaurantRecommendationPage() {
  const navigate = useNavigate();
  const [places, setPlaces] = useState([]);
  const [aiComment, setAiComment] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [hasLoadedFromStorage, setHasLoadedFromStorage] = useState(false);

  const tasteProfile = JSON.parse(localStorage.getItem("tasteProfile")); // 로컬스토리지에 저장된 맛집 성향 가져오기
  const VITE_API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const handleRetry = () => {
    // Clear saved localStorage data before retrying
    localStorage.removeItem("savedAiComment");
    localStorage.removeItem("savedPlaces");
    setHasLoadedFromStorage(false);
    if (tasteProfile) {
      setIsLoading(true);
      axios
        .post(`${VITE_API_BASE_URL}/ai/restaurant`, {
          companion: tasteProfile.companions,
          foodPreference: tasteProfile.foodPreference,
          atmospheres: tasteProfile.atmospheres,
          city: tasteProfile.city,
          region: tasteProfile.region,
        })
        .then((res) => {
          setAiComment(res.data.aiComment);
          setPlaces(res.data.places);
          // Save to localStorage
          localStorage.setItem("savedAiComment", res.data.aiComment);
          localStorage.setItem("savedPlaces", JSON.stringify(res.data.places));
          setIsLoading(false);
        })
        .catch((err) => {
          console.error("맛집 추천 API 호출 실패", err);
          setIsLoading(false);
        });
    }
  };

  useEffect(() => {
    const savedPlaces = localStorage.getItem("savedPlaces");
    const savedComment = localStorage.getItem("savedAiComment");
    if (savedPlaces && savedComment) {
      setPlaces(JSON.parse(savedPlaces));
      setAiComment(savedComment);
      setHasLoadedFromStorage(true);
    } else {
      handleRetry();
    }
  }, []);

  if (isLoading && !hasLoadedFromStorage)
    return (
      <>
        <Header />
        <LottieAnimation />
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
          <p className="text-blue-700 mt-1">{aiComment}</p>
        </div>

        {/* api 응답값 뿌려주기 */}
        {places.map((place, index) => (
          <div key={index} className="bg-white shadow-md rounded-xl p-4 mb-6">
            <div className="flex gap-4">
              <img
                src={place.imageUrl}
                alt="맛집 썸네일"
                className="bg-blue-100 w-32 h-32 flex items-center justify-center text-blue-400 rounded-lg"
              />
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
                        state: {
                          placeId: place.placeId,
                          companions: tasteProfile?.companions,
                          atmospheres: tasteProfile?.atmospheres,
                        },
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

        {/* Bottom Buttons */}
        <div className="flex flex-wrap gap-2 mt-10">
          <button
            onClick={handleRetry}
            className="flex items-center gap-2 bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            다시 추천받기
          </button>
          <button
            onClick={() => navigate("/RestaurantInput")}
            className="bg-white text-blue-700 border border-blue-400 px-4 py-2 rounded-lg"
          >
            성향 입력 다시하기
          </button>
        </div>
      </div>
      <Footer />
    </>
  );
}