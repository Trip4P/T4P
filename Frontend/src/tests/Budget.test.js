import React, { useState, useEffect } from "react";
import { Doughnut } from "react-chartjs-2";
import axios from "axios";
import { render, screen } from "@testing-library/react";
import Budget from "../pages/Budget.jsx";
import { MemoryRouter } from "react-router-dom";

jest.mock("axios");

global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
}

describe("예산 계산 페이지 테스트", () => {
  test("예산 정보가 올바르게 렌더링됨", async () => {
    const travelPlanData = {
      plans: [
        {
          day: 1,
          schedule: [
            {
              time: "09:00",
              placeType: "체크아웃",
              place: "호텔 부산",
              placeId: 213,
            },
            {
              time: "12:00",
              placeType: "점심 식사",
              place: "청춘 횟집",
              placeId: 214,
            },
          ],
        },
      ],
      peopleCount: 1,
    };

    localStorage.setItem("travelPlan", JSON.stringify(travelPlanData));

    const mockApiResponse = {
      data: {
        totalBudget: 1150000,
        categoryBreakdown: [
          { 교통: 300000 },
          { 숙박: 400000 },
          { 식비: 250000 },
          { 관광: 200000 },
        ],
        aiComment: "여행지 물가 기준으로는 꽤 여유로운 편이에요. 원하는 곳 마음껏 즐기세요!",
      },
    };

    axios.get.mockResolvedValueOnce(mockApiResponse);

    render(
      <MemoryRouter>
        <Budget />
      </MemoryRouter>
    );

    expect(await screen.findByText(/₩\s*1,150,000/)).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes("교통"))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes("숙박"))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes("식비"))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes("관광"))).toBeInTheDocument();
    expect(screen.getByText((content) => content.includes("여행지 물가 기준으로는 꽤 여유로운 편이에요"))).toBeInTheDocument();
  });
});