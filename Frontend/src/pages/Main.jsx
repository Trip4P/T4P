import React from "react";
import { Link } from "react-router-dom";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function MainPage() {
  return (
    <div className="bg-white text-gray-800">
      <Header />

      {/* Hero Section */}
      <section className="flex flex-col lg:flex-row items-center justify-between px-8 py-16 bg-gray-50">
        <div className="max-w-xl space-y-4">
          <h1 className="text-3xl font-bold leading-tight">
            AI가 만드는 맞춤형 스마트 여행 플래너
          </h1>
          <p className="text-sm text-gray-600">
            당신의 여행 스타일을 분석하여 최적의 여행 일정을 만들어 드립니다.
            맛집 추천부터 예산 계산까지, 모든 여행 계획을 한번에!
          </p>
          <button className="mt-4 px-6 py-2 bg-blue-600 text-white text-sm rounded">
            <Link to="/TravelStyleForm">
            여행 일정 추천 받기
          </Link>
          </button>
        </div>
        <img
          src="https://via.placeholder.com/400x250"
          alt="hero"
          className="mt-8 lg:mt-0 lg:ml-16 rounded"
        />
      </section>

      {/* Features */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 px-8 py-12">
        <div className="bg-white shadow-md rounded p-6 text-center">
          <h3 className="font-semibold mb-2">성향 분석</h3>
          <p className="text-sm text-gray-600">
            여행 스타일 분석에 맞춘 여행지를 추천합니다.
          </p>
        </div>
        <div className="bg-white shadow-md rounded p-6 text-center">
          <h3 className="font-semibold mb-2">일정 자동 생성</h3>
          <p className="text-sm text-gray-600">
            여행 일정을 AI가 자동으로 생성해드립니다.
          </p>
        </div>
        <div className="bg-white shadow-md rounded p-6 text-center">
          <h3 className="font-semibold mb-2">맛집 추천</h3>
          <p className="text-sm text-gray-600">
            현지 맛집 정보를 기반으로 맛집을 추천해드립니다.
          </p>
        </div>
      </section>

      {/* Popular Destinations */}
      <section className="px-8 pb-12">
        <h2 className="text-lg font-semibold mb-4">인기 여행지</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className="bg-gray-300 h-32 rounded text-center text-white flex items-center justify-center"
            >
              image
            </div>
          ))}
        </div>
      </section>

      {/* How to Use */}
      <section className="bg-gray-50 py-12 px-8">
        <h2 className="text-lg font-semibold text-center mb-8">이용 방법</h2>
        <div className="flex flex-col md:flex-row justify-center gap-8 text-center">
          <div>
            <div className="text-blue-600 font-bold text-2xl mb-2">1</div>
            <p className="font-semibold mb-1">여행 스타일 입력</p>
            <p className="text-sm text-gray-600">
              여행 스타일과 관심지를 선택해주세요.
            </p>
          </div>
          <div>
            <div className="text-blue-600 font-bold text-2xl mb-2">2</div>
            <p className="font-semibold mb-1">AI 분석</p>
            <p className="text-sm text-gray-600">
              AI가 스타일을 분석하여 일정을 구성합니다.
            </p>
          </div>
          <div>
            <div className="text-blue-600 font-bold text-2xl mb-2">3</div>
            <p className="font-semibold mb-1">맞춤 여행 완성</p>
            <p className="text-sm text-gray-600">
              일정, 맛집, 예산이 포함된 여행 계획 완성!
            </p>
          </div>
        </div>
      </section>

      <section className="py-12 px-8 text-center bg-blue-50">
        <h2 className="text-lg font-semibold mb-2">
          나만의 완벽한 여행을 시작해보세요
        </h2>
        <p className="text-sm text-gray-700 mb-4">
          AI와 함께 특별한 여행을 계획해보세요.
        </p>
        <button className="px-6 py-2 bg-blue-600 text-white rounded">
          <Link to="/TravelStyleForm">
            지금 바로 시작하기
          </Link>
        </button>
      </section>

      <Footer />
    </div>
  );
}
