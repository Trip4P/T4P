import { render, screen, waitFor } from "@testing-library/react";
import PlaceDetailPage from "../pages/PlaceDetail";
import { MemoryRouter } from "react-router-dom";
import axios from "axios";

jest.mock("axios");

const mockResponse = {
  data: {
    image: "image_url",
    place: "오션뷰 카페",
    tags: ["카페", "오션뷰"],
    businessHours: "09:00 ~ 21:00",
    price: "인당 약 15,000원",
    address: "해운대구 달맞이길~~",
    phone: "051-610-4882",
    averageRate: "4.5",
    reviewCount: "1204",
    aiComment: "감성 여행에 안성 맞춤이에요~~",
    reviewHighlights: {
      title: "뷰가 예술이에요",
      date: "2025.05.10",
      review: "바다가 한눈에 보이는 뷰가 좋았어요~~.",
    },
    satisfaction: "87",
    reviewKeywords: ["뷰맛집", "직원친절", "대기주의"],
    위치_정보: {
      lat: "37.253421432",
      lon: "127.43531423",
    },
  },
};

test("장소 상세 페이지가 API 데이터로 잘 렌더링됨", async () => {
  axios.get.mockResolvedValueOnce(mockResponse);

  render(
    <MemoryRouter initialEntries={[{ pathname: "/place-detail", state: { placeId: "123" } }]}>
      <PlaceDetailPage />
    </MemoryRouter>
  );

  await waitFor(() => {
    expect(screen.getByText("오션뷰 카페")).toBeInTheDocument();
    expect(screen.getByText("카페")).toBeInTheDocument();
    expect(screen.getByText("09:00 ~ 21:00")).toBeInTheDocument();
    expect(screen.getByText("인당 약 15,000원")).toBeInTheDocument();
    expect(screen.getByText("감성 여행에 안성 맞춤이에요~~")).toBeInTheDocument();
    expect(screen.getByText("뷰가 예술이에요")).toBeInTheDocument();
    expect(screen.getByText(/87%/)).toBeInTheDocument();
    expect(screen.getByText("#뷰맛집")).toBeInTheDocument();
  });
});
