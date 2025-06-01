import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import axios from "axios";
import RestaurantDetailPage from "../pages/RestaurantDetail";

jest.mock("axios");

describe("RestaurantDetailPage", () => {
  test("API 응답값이 화면에 잘 표시되는지 테스트", async () => {
    axios.get.mockResolvedValueOnce({
      data: {
        place: "오션뷰 카페",
        tags: ["카페", "해운대"],
        businessHours: "09:00 ~ 21:00",
        price: "인당 약 15,000원",
        address: "부산광역시 해운대구 달맞이길 123",
        phone: "051-123-4567",
        averageRate: "4.5",
        reviewCount: "1204",
        aiComment: "감성 여행에 안성맞춤이에요~~",
        reviewHighlights: {
          title: "뷰가 예술이에요",
          date: "2025.05.10",
          review: "바다가 한눈에 보이는 뷰가 좋았어요~~.",
        },
        satisfaction: "87",
        reviewKeywords: ["뷰맛집", "직원친절", "대기주의"],
        위치정보: {
          lat: 37.253421432,
          lon: 127.43531423,
        },
      },
    });

    render(
      <MemoryRouter initialEntries={["/RestaurantDetail/342"]}>
        <Routes>
          <Route path="/RestaurantDetail/:placeId" element={<RestaurantDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText("오션뷰 카페")).toBeInTheDocument();
    expect(screen.getByText("감성 여행에 안성맞춤이에요~~")).toBeInTheDocument();
    expect(screen.getByText("#뷰맛집")).toBeInTheDocument();
    expect(screen.getByText("09:00 ~ 21:00")).toBeInTheDocument();
    expect(screen.getByText("인당 약 15,000원")).toBeInTheDocument();
    expect(screen.getByText("부산광역시 해운대구 달맞이길 123")).toBeInTheDocument();
    expect(screen.getByText("051-123-4567")).toBeInTheDocument();
  });
});
