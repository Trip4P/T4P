import { render, screen, waitFor } from "@testing-library/react";
import TravelPlan from "../pages/TravelPlan";
import "@testing-library/jest-dom";
import axios from "axios";
import { BrowserRouter } from "react-router-dom";

jest.mock("axios");
jest.mock("../components/GoogleMapView", () => {
  return jest.fn(() => <div>Mock Google Map View</div>); // Render a simple div
});

const mockApiResponse = {
  data: {
    startDate: '2025.05.13',
    endDate: '2025.05.15',
    aiEmpathy:
      "와아~ 지금 기분이 너무 좋은 거잖아? 😆이제는 나를 위한 힐링 여행 딱 갈 타이밍이네!그럼 이 기분 그대로 이어서, 서울에서 2박 3일 동안 제대로 즐길 수 있는 기분 최고 힐링&뿌듯 여행 코스 추천해줄게! ✨",
    tags: ["미식", "감성", "바다", "여유"],
    plans: [
      {
        day: 1,
        schedule: [
          {
            time: "09:00",
            placeType: "체크아웃",
            place: "호텔 부산",
            placeId: "213",
            aiComment: "오션뷰 객실에서 여유로운 시작",
          },
          {
            time: "12:00",
            placeType: "점심 식사",
            place: "청춘 횟집",
            placeId: "214",
            aiComment: "현지인이 추천하는 신선한 회와 물회",
          },
        ],
      },
    ],
  },
};

describe("TravelPlan Component", () => {
  test("여행 일정 추천 from API data", async () => {
    axios.get.mockResolvedValueOnce(mockApiResponse);

    render(
      <BrowserRouter>
        <TravelPlan />
      </BrowserRouter>
    );

    // aiEmpathy 문구 확인
    await waitFor(() =>
      expect(screen.getByText(/힐링 여행/)).toBeInTheDocument()
    );

    // 일정의 장소명이 화면에 나오는지 확인
    expect(await screen.findByText(/청춘 횟집/)).toBeInTheDocument();
    expect(await screen.findByText(/호텔 부산/)).toBeInTheDocument();

    // 태그가 표시되는지 확인
    const tags = await screen.findAllByText(text => text.includes("미식"));
    expect(tags.length).toBeGreaterThan(0);
    screen.debug();
  });
});