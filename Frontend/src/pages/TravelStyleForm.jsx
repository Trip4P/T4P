import React from "react";
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
  const [destination, setDestination] = useState("");
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  return (
    <>
      <Header />
      <div className="max-w-4xl mx-auto py-16 px-4">
        <h1 className="text-2xl font-bold text-center mb-2">여행 성향 분석</h1>
        <p className="text-center text-gray-500 mb-10">
          나의 여행 스타일을 분석하여 맞춤형 여행 코스를 추천해드립니다.
        </p>

        {/* 목적지 입력 */}
        <div className="bg-gray-50 rounded-xl p-6 mb-10">
          <h2 className="text-lg font-semibold mb-4">여행 목적지</h2>
          <input type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            className="w-full border border-gray-300 rounded px-4 py-2"
            placeholder="ex) 서울 잠실"
          />
        </div>
        
        <div className="bg-gray-50 rounded-xl p-6 mb-10">
          <h2 className="text-lg font-semibold mb-4">여행 기간</h2>
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
                className="border border-gray-300 rounded px-4 py-2"
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
                className="border border-gray-300 rounded px-4 py-2"
              />
            </div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-xl p-6 mb-10">
          <h2 className="text-lg font-semibold mb-4">현재 나의 감정</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {categories.map((item) => (
              <label key={item} className="flex items-center gap-2">
                <input type="checkbox" className="form-checkbox accent-black" />
                <span>{item}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="bg-gray-50 rounded-xl p-6 mb-10">
          <h2 className="text-lg font-semibold mb-4">누구와 떠나나요</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {companions.map((item) => (
              <label key={item} className="flex items-center gap-2">
                <input type="checkbox" className="form-checkbox accent-black" />
                <span>{item}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="text-center">
          <button
            onClick={() => navigate("/TravelPlan")}
            className="bg-blue-600 text-white rounded px-6 py-3 hover:bg-blue-800 transition"
          >
            분석 시작하기
          </button>
        </div>
      </div>
    </>
  );
}
