import { render, screen, fireEvent, within } from "@testing-library/react";
import TravelStyleForm from "../src/pages/TravelStyleForm";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";

describe("TravelStyleForm", () => {
  beforeEach(() => {
    localStorage.clear(); // 초기화
  });

  test("사용자 입력 정보가 localStorage에 저장된다", async () => {
    render(
      <MemoryRouter>
        <TravelStyleForm />
      </MemoryRouter>
    );

    const user = userEvent.setup();

    // 출발지와 목적지 입력
    fireEvent.change(screen.getByPlaceholderText("ex) 서울역"), {
      target: { value: "서울역" },
    });
    fireEvent.change(screen.getByPlaceholderText("ex) 잠실"), {
      target: { value: "부산역" },
    });

    // 여행 시작일 입력
    await user.click(screen.getByPlaceholderText("시작일 선택"));
    const startPopup = screen.getByRole("dialog");
    const startCalendar = within(startPopup);
    await user.click(startCalendar.getByText("1")); // 1일 클릭

    // // 여행 종료일 입력
    await user.click(screen.getByPlaceholderText("종료일 선택"));
    const endPopup = screen.getByRole("dialog");
    const endCalendar = within(endPopup);
    await user.click(endCalendar.getByText("3")); // 3일 클릭

    // 감정 체크 (예: "설레는"이라는 감정 체크박스가 있다고 가정)
    fireEvent.click(screen.getByLabelText("설레는"));

    // 인원 수 입력
    fireEvent.change(screen.getByLabelText("인원수"), {
      target: { value: 2 },
    });

    // 버튼 클릭
    fireEvent.click(screen.getByText("분석 시작하기"));

    // 로컬스토리지에 저장된 데이터 확인
    const stored = JSON.parse(localStorage.getItem("travelStyle"));
    // console.log("stored: ", stored);
    expect(stored.departure).toBe("서울역");
    expect(stored.destination).toBe("부산역");
    expect(stored.startDate).toBeDefined();
    expect(stored.endDate).toBeDefined();
    expect(stored.peopleCount).toBe(2);
    expect(stored.emotion).toContain("설레는");
  });
});