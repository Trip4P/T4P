import { useNavigate } from "react-router-dom";
import { useState } from "react";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

const categories = [
  "😊 기쁜",
  "💗 설레는",
  "🙂 평범한",
  "😮 놀란",
  "🤢 불쾌한",
  "😨 두려운",
  "😢 슬픈",
  "😡 화나는",
];

const companionBoxes = [
  "👤 혼자",
  "👥 친구와",
  "👩‍❤️‍👨연인과",
  "👫 배우자와",
  "👶 아이와",
  "🧑‍💼👨🏻‍💼부모님과",
];

const formatDateKorean = (date) =>
  date
    ?.toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    })
    .replace(/\. /g, "-")
    .replace(/\./g, "");

export default function TravelStyleForm() {
  const navigate = useNavigate();
  const [startCity, setStartCity] = useState("");
  const [endCity, setEndCity] = useState("");
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [emotions, setEmotions] = useState([]);
  const [companions, setCompanions] = useState([]);
  const [peopleCount, setPeopleCount] = useState(1);

  return (
    <>
      <Header />
      <div className="min-h-screen bg-gradient-to-b from-blue-100 to-white p-6">
        <h1 className="text-3xl font-bold text-center text-blue-900 mb-2">
          여행 성향 분석
        </h1>
        <p className="text-center text-blue-700 mb-10">
          나의 여행 스타일을 분석하여 맞춤형 여행 코스를 추천해드립니다.
        </p>
        <div className="max-w-3xl mx-auto">
          <div className="bg-blue-50 p-6 rounded-xl shadow-md mb-6">
            {/* 목적지 입력 */}
            <h2 className="text-lg font-semibold text-blue-700 mb-4">
              여행 목적지
            </h2>
            <input
              type="text"
              value={endCity}
              onChange={(e) => setEndCity(e.target.value)}
              className="w-full border border-blue-300 rounded px-4 py-2"
              placeholder="ex) 송파구"
            />
          </div>

          <div className="bg-blue-50 p-6 rounded-xl shadow-md mb-6">
            <h2 className="text-lg font-semibold text-blue-700 mb-4">
              여행 기간
            </h2>
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex flex-col">
                <label className="mb-1 font-medium">여행 시작일</label>
                <DatePicker
                  selected={startDate}
                  onChange={(date) => setStartDate(date)}
                  selectStart
                  startDate={startDate}
                  endDate={endDate}
                  placeholderText="시작일 선택"
                  dateFormat="yyyy-MM-dd"
                  className="border border-blue-300 rounded px-4 py-2"
                />
              </div>

              <div className="flex flex-col">
                <label className="mb-1 font-medium">여행 종료일</label>
                <DatePicker
                  selected={endDate}
                  onChange={(date) => setEndDate(date)}
                  selectsEnd
                  startDate={startDate}
                  endDate={endDate}
                  placeholderText="종료일 선택"
                  dateFormat="yyyy-MM-dd"
                  className="border border-blue-300 rounded px-4 py-2"
                />
              </div>
            </div>
          </div>

          <div className="bg-blue-50 p-6 rounded-xl shadow-md mb-6">
            <h2 className="text-lg font-semibold text-blue-700 mb-4">
              현재 나의 감정
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {categories.map((item) => (
                <label key={item} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    className="form-checkbox accent-black"
                    checked={emotions.includes(item)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setEmotions([...emotions, item]);
                      } else {
                        setEmotions(emotions.filter((i) => i !== item));
                      }
                    }}
                  />
                  <span>{item}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="bg-blue-50 p-6 rounded-xl shadow-md mb-6">
            <h2 className="text-lg font-semibold text-blue-700 mb-4">
              누구와 떠나나요
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {companionBoxes.map((item) => (
                <label key={item} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    className="form-checkbox accent-black"
                    checked={companions.includes(item)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setCompanions([...companions, item]);
                      } else {
                        setCompanions(companions.filter((i) => i !== item));
                      }
                    }}
                  />
                  <span>{item}</span>
                </label>
              ))}
            </div>

            <h2 className="text-lg font-semibold text-blue-700 mt-5 mb-4">
              몇 명이서 떠나나요
            </h2>
            <div className="flex items-center space-x-4">
              {/* <label className="text-gray-700 font-medium">인원수:</label> */}
              <input
                type="number"
                min="1"
                value={peopleCount}
                onChange={(e) => setPeopleCount(Number(e.target.value))}
                aria-label="인원수"
                className="border border-gray-300 rounded-lg px-4 py-2 w-28 focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
          </div>

          <div className="text-center">
            <button
              onClick={() => {
                const travelStyleDate = {
                  startCity,
                  endCity,
                  startDate: startDate ? formatDateKorean(startDate) : null,
                  endDate: endDate ? formatDateKorean(endDate) : null,
                  emotions,
                  companions,
                  peopleCount,
                };
                // 로컬 스토리지 저장
                localStorage.setItem(
                  "travelStyle",
                  JSON.stringify(travelStyleDate)
                );
                localStorage.removeItem("travelPlan");
                navigate("/TravelPlan");
              }}
              className="bg-blue-600 text-white rounded px-6 py-3 hover:bg-blue-800 transition"
            >
              분석 시작하기
            </button>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
}
