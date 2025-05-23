import React from "react";
import Header from "../components/Header";

export default function RestaurantDetailPage() {
  return (
    <>
      <Header/>
    <div className="bg-white text-gray-800">
      {/* 헤더 이미지 */}
      <div className="w-full h-64 bg-gradient-to-b from-blue-400 to-blue-600 flex items-center justify-center">
        <div className="w-24 h-24 bg-white rounded-md flex items-center justify-center">
          <span className="text-blue-600 font-bold text-xl">이미지</span>
        </div>
      </div>

      {/* 가게 정보 */}
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold text-blue-800 mb-2">오션뷰 카페</h1>
        <div className="flex gap-2 mb-4">
          <span className="bg-blue-100 text-blue-600 px-2 py-1 rounded text-sm">카페</span>
          <span className="bg-blue-100 text-blue-600 px-2 py-1 rounded text-sm">해운대</span>
          <span className="bg-blue-100 text-blue-600 px-2 py-1 rounded text-sm">관광지</span>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm text-gray-700 mb-6">
          <div>
            <p className="font-semibold">영업시간</p>
            <p>09:00 ~ 21:00 (연중무휴)</p>
          </div>
          <div>
            <p className="font-semibold">가격대</p>
            <p>인당 약 15,000원</p>
          </div>
          <div>
            <p className="font-semibold">주소</p>
            <p>부산광역시 해운대구 달맞이길 123</p>
          </div>
          <div>
            <p className="font-semibold">대표 메뉴</p>
            <p>샐먼연어덮밥, 아메리카노</p>
          </div>
          <div>
            <p className="font-semibold">평균 평점</p>
            <p>4.5 (1,204개 리뷰)</p>
          </div>
        </div>

        {/* AI 추천 포인트 */}
        <div className="bg-blue-50 rounded-lg p-4 mb-6">
          <h2 className="text-blue-700 font-semibold mb-2">AI 추천 포인트</h2>
          <p>"현지인들도 자주 찾는 바다 전망 카페입니다. 특히 오후 3~5시쯤 햇살과 풍경이 좋아 감성 여행에 안성맞춤이에요."</p>
        </div>

        {/* 리뷰 하이라이트 */}
        <div className="mb-6">
          <h2 className="text-blue-700 font-semibold mb-4">리뷰 하이라이트</h2>
          <div className="flex items-start gap-4 mb-2">
            <div className="w-10 h-10 bg-gray-200 rounded-full" />
            <div>
              <p className="font-semibold">뷰가 예술이에요</p>
              <p className="text-sm text-gray-500 mb-1">2025.05.10</p>
              <p>바다가 한눈에 보이는 뷰가 정말 좋았어요. 직원분들도 친절하시고 음식도 맛있었습니다.</p>
            </div>
          </div>
          <div className="mt-2">
            <p className="text-sm mb-1">만족도 <span className="font-semibold">87%</span></p>
            <div className="w-full h-2 bg-gray-200 rounded-full">
              <div className="w-[87%] h-full bg-blue-500 rounded-full" />
            </div>
          </div>
          <div className="mt-3 flex gap-2 flex-wrap text-sm">
            <span className="bg-blue-100 text-blue-600 px-2 py-1 rounded">#바다전망</span>
            <span className="bg-blue-100 text-blue-600 px-2 py-1 rounded">#직원친절</span>
            <span className="bg-blue-100 text-blue-600 px-2 py-1 rounded">#데이트카페</span>
          </div>
        </div>

        {/* 위치 정보 */}
        <div className="bg-gray-100 rounded-lg p-4">
          <h2 className="text-blue-700 font-semibold mb-2">위치 정보</h2>
          <div className="w-full h-60 bg-gray-300 rounded mb-4 flex items-center justify-center text-gray-500">
            지도 영역
          </div>
          <div className="flex gap-4">
            <button className="flex-1 py-2 px-4 bg-white border border-blue-500 text-blue-600 rounded hover:bg-blue-50">지도 보기</button>
            <button className="flex-1 py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600">길찾기 (구현할지 미정)</button>
          </div>
        </div>
      </div>
      </div>
    </>
  );
}