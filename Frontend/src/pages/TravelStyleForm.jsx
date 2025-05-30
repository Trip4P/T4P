import { useNavigate } from "react-router-dom";
import { useState } from "react";
import Header from "../components/Header";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

const categories = [
  "기쁜",
  "설레는",
  "평범한",
  "놀란",
  "불쾌한",
  "두려운",
  "슬픈",
  "화나는",
];

const companions = [
  "혼자",
  "친구와",
  "연인과",
  "배우자와",
  "아이와",
  "부모님과",
];

export default function TravelStyleForm() {
  const navigate = useNavigate();
  const [departure, setDeparture] = useState("");
  const [destination, setDestination] = useState("");
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [emotion, setEmotion] = useState([]);
  const [companion, setCompanion] = useState([]);
  const [peopleCount, setPeopleCount] = useState(1);

  return (
    <>
      <Header />
      <div className="max-w-4xl mx-auto py-16 px-4">
        <h1 className="text-2xl font-bold text-center mb-2">여행 성향 분석</h1>
        <p className="text-center text-gray-500 mb-10">
          나의 여행 스타일을 분석하여 맞춤형 여행 코스를 추천해드립니다.
        </p>

        {/* 출발지 입력 */}
        <div className="bg-gray-50 rounded-xl p-6 mb-10">
          <h2 className="text-lg font-semibold mb-4">여행 출발지</h2>
        {/* 출발지 입력 */}
        <input
          type="text"
          data-testid="input-departure"
          value={departure}
          onChange={(e) => setDeparture(e.target.value)}
          className="w-full border border-gray-300 rounded px-4 py-2"
          placeholder="ex) 서울역"
        />

        {/* 목적지 입력 */}
        <input
          type="text"
          data-testid="input-destination"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          className="w-full border border-gray-300 rounded px-4 py-2"
          placeholder="ex) 잠실"
        />

        {/* 여행 시작일 */}
        <DatePicker
          selected={startDate}
          onChange={(date) => setStartDate(date)}
          selectsStart
          startDate={startDate}
          endDate={endDate}
          placeholderText="시작일 선택"
          dateFormat="yyyy-MM-dd"
          customInput={
            <input
              data-testid="date-start"
              className="border border-gray-300 rounded px-4 py-2"
              /> 
          }
        />

        {/* 여행 종료일 */}
        <DatePicker
          selected={endDate}
          onChange={(date) => setEndDate(date)}
          selectsEnd
          startDate={startDate}
          endDate={endDate}
          placeholderText="종료일 선택"
          dateFormat="yyyy-MM-dd"
          customInput={
            <input
            className="border border-gray-300 rounded px-4 py-2"
            data-testid="date-end"
            />
          }
        />

        {/* 감정 체크박스 */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {categories.map((item) => (
            <label key={item} className="flex items-center gap-2">
              <input
                type="checkbox"
                data-testid={`emotion-${item}`}
                className="form-checkbox accent-black"
                checked={emotion.includes(item)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setEmotion([...emotion, item]);
                  } else {
                    setEmotion(emotion.filter((i) => i !== item));
                  }
                }}
              />
              <span>{item}</span>
            </label>
          ))}
        </div>

        {/* 동행자 체크박스 */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {companions.map((item) => (
            <label key={item} className="flex items-center gap-2">
              <input
                type="checkbox"
                data-testid={`companion-${item}`}
                className="form-checkbox accent-black"
                checked={companion.includes(item)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setCompanion([...companion, item]);
                  } else {
                    setCompanion(companion.filter((i) => i !== item));
                  }
                }}
              />
              <span>{item}</span>
            </label>
          ))}
        </div>


        {/* 인원수 입력 */}
        <input
          type="number"
          min="1"
          data-testid="input-people-count"
          value={peopleCount}
          onChange={(e) => setPeopleCount(Number(e.target.value))}
          aria-label="인원수"
          className="border border-gray-300 rounded-lg px-4 py-2 w-28 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />

        {/* 분석 시작하기 버튼 */}
        <button
          data-testid="btn-analyze"
          onClick={() => {
            const travelStyleDate = {
              departure,
              destination,
              startDate: startDate ? startDate.toISOString().split("T")[0] : null,
              endDate: endDate ? endDate.toISOString().split("T")[0] : null,
              emotion,
              companion,
              peopleCount,
            };
            localStorage.setItem("travelStyle", JSON.stringify(travelStyleDate));
            navigate("/TravelPlan");
          }}
          className="bg-blue-600 text-white rounded px-6 py-3 hover:bg-blue-800 transition"
        >
          분석 시작하기
        </button>

        </div>
      </div>
    </>
  );
}