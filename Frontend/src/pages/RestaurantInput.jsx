import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";

const preferences = {
  companions: ["혼자", "친구와", "연인과", "배우자와", "아이와", "부모님과"],
  foodTypes: ["한식", "일식", "중식", "양식", "동남아식"],
  atmospheres: [
    "데이트",
    "비즈니스 미팅",
    "기념일",
    "단체회식",
    "가족모임",
    "뷰 맛집",
    "상견례",
    "조용한",
    "모던한",
    "전통적인",
  ],
};

const CheckboxGroup = ({ title, items, selectedItems, onChange }) => (
  <div className="bg-blue-50 p-6 rounded-xl shadow-md mb-6">
    <h2 className="text-lg font-semibold text-blue-700 mb-4">{title}</h2>
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {items.map((item, idx) => (
        <label key={idx} className="flex items-center space-x-2">
          <input
            type="checkbox"
            name={title}
            value={item}
            checked={selectedItems.includes(item)}
            onChange={(e) => {
              if (e.target.checked) {
                onChange([...selectedItems, item]);
              } else {
                onChange(selectedItems.filter((i) => i !== item));
              }
            }}
            className="accent-blue-600"
          />
          <span className="text-blue-900">{item}</span>
        </label>
      ))}
    </div>
  </div>
);

export default function TasteProfilePage() {
  const navigate = useNavigate();

  const [selectedCompanions, setSelectedCompanions] = useState([]);
  const [selectedFoodTypes, setSelectedFoodTypes] = useState([]);
  const [selectedAtmospheres, setSelectedAtmospheres] = useState([]);
  const [city, setCity] = useState("");
  const [region, setRegion] = useState("");

  return (
    <>
      <Header />
      <div className="min-h-screen bg-gradient-to-b from-blue-100 to-white p-6">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold text-center text-blue-900 mb-2">
            맛집 성향 분석
          </h1>
          <p className="text-center text-blue-700 mb-8">
            나의 맛집 스타일을 분석하여 맞춤형 맛집을 추천해드립니다.
          </p>

          <CheckboxGroup
            title="누구와 떠나나요"
            items={preferences.companions}
            selectedItems={selectedCompanions}
            onChange={setSelectedCompanions}
          />
          <CheckboxGroup
            title="선호하는 음식 종류는?"
            items={preferences.foodTypes}
            selectedItems={selectedFoodTypes}
            onChange={setSelectedFoodTypes}
          />
          <CheckboxGroup
            title="선호하는 분위기는?"
            items={preferences.atmospheres}
            selectedItems={selectedAtmospheres}
            onChange={setSelectedAtmospheres}
          />

          <div className="bg-blue-50 p-6 rounded-xl shadow-md mb-6">
            <h2 className="text-lg font-semibold text-blue-700 mb-4">여행 도시</h2>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="ex) 서울"
              className="w-full border border-gray-300 rounded px-4 py-2"
            />
          </div>

          <div className="bg-blue-50 p-6 rounded-xl shadow-md mb-6">
            <h2 className="text-lg font-semibold text-blue-700 mb-4">도시 내 지역</h2>
            <input
              type="text"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              placeholder="ex) 해운대"
              className="w-full border border-gray-300 rounded px-4 py-2"
            />
          </div>

          <div className="text-center mt-10">
            <button
              onClick={() => {
                const tasteProfile = {
                  companions: selectedCompanions,
                  foodTypes: selectedFoodTypes,
                  atmospheres: selectedAtmospheres,
                  city,
                  region,
                };
                localStorage.setItem("tasteProfile", JSON.stringify(tasteProfile));
                navigate("/RestaurantRecommend");
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-full shadow-md transition"
            >
              분석 시작하기
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
