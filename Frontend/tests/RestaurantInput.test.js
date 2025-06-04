import { render, screen, fireEvent } from "@testing-library/react";
import TasteProfilePage from "../src/pages/RestaurantInput";
import { MemoryRouter } from "react-router-dom";

describe("맛집 성향 테스트", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test("사용자 입력이 localStorage에 저장된다", () => {
    render(
      <MemoryRouter>
        <TasteProfilePage />
      </MemoryRouter>
    );

    // checkbox 클릭
    fireEvent.click(screen.getByLabelText("친구와"));
    fireEvent.click(screen.getByLabelText("한식"));
    fireEvent.click(screen.getByLabelText("데이트"));

    // 여행 도시, 도시 내 지역 입력
    fireEvent.change(screen.getByPlaceholderText("ex) 서울"), {
      target: { value: "서울" },
    });
    fireEvent.change(screen.getByPlaceholderText("ex) 해운대"), {
      target: { value: "여의도"},
    })

    // 버튼 클릭
    fireEvent.click(screen.getByText("분석 시작하기"));

    const stored = JSON.parse(localStorage.getItem("tasteProfile"));

    expect(stored).toEqual({
      companions: ["친구와"],
      foodTypes: ["한식"],
      atmospheres: ["데이트"],
      city: "서울",
      region: "여의도",
    });
  });
});