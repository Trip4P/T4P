import { render, screen, waitFor } from "@testing-library/react";
import RestaurantRecommendationPage from "../pages/RestaurantRecommend";
import { MemoryRouter } from "react-router-dom";
import axios from "axios";

jest.mock("axios");
jest.mock("../components/GoogleMapView", () => () => <div data-testid="mock-map">MockMap</div>);

describe("RestaurantRecommend 페이지", () => {
  beforeEach(() => {
    localStorage.setItem(
      "tasteProfile",
      JSON.stringify({
        companions: ["아이와", "배우자와"],
        foodTypes: ["한식", "일식"],
        atmospheres: ["데이트", "뷰 맛집"],
        city: "부산",
        region: "해운대",
      })
    );
  });

  test("맛집 추천 API 결과가 화면에 잘 렌더링된다", async () => {
    const mockResponse = {
      data: {
        aiComment: "뷰 맛집이 어울리는 맛집으로 추천했어요!",
        places: [
          {
            name: "오레노라멘",
            aiFoodComment: "송리단길 국물이 맛있는 라멘집",
            tags: ["뷰맛집", "현지맛집"],
            placeId: 342,
          },
          {
            name: "다운타우너",
            aiFoodComment: "패티가 두툼한 수제버거 맛집",
            tags: ["미식", "수제버거"],
            placeId: 432,
          },
        ],
      },
    };

    axios.get.mockResolvedValueOnce(mockResponse);

    render(
      <MemoryRouter>
        <RestaurantRecommendationPage />
      </MemoryRouter>
    );

    // AI 코멘트가 보이는지 확인
    await waitFor(() => {
      expect(screen.getByText("뷰 맛집이 어울리는 맛집으로 추천했어요!")).toBeInTheDocument();
    });

    // 맛집 이름과 태그, 설명이 보이는지 확인
    expect(screen.getByText("오레노라멘")).toBeInTheDocument();
    expect(screen.getByText("다운타우너")).toBeInTheDocument();
    expect(screen.getByText("송리단길 국물이 맛있는 라멘집")).toBeInTheDocument();
    expect(screen.getByText("패티가 두툼한 수제버거 맛집")).toBeInTheDocument();
    expect(screen.getByText("#뷰맛집")).toBeInTheDocument();
    expect(screen.getByText("#수제버거")).toBeInTheDocument();
  });
});