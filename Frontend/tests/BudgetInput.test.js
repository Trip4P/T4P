import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import BudgetInputPage from "../src/pages/BudgetInput";
import { MemoryRouter } from "react-router-dom";
import axios from "axios";

class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

global.ResizeObserver = ResizeObserver;

jest.mock("axios");

describe("BudgetInputPage", () => {
  test("일정 추천 없는 예산 페이지(시나리오B) 테스트", async () => {
    const mockResponse = {
      data: {
        total_budget: 320000,
        breakdown: [
          { food: 60000 },
          { transport: 40000 },
          { activities: 70000 },
        ],
        aiComment: "AI코멘트",
      },
    };

    axios.post.mockResolvedValueOnce(mockResponse);

    render(
      <MemoryRouter>
        <BudgetInputPage />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText("ex) 서울"), {
      target: { value: "서울" },
    });
    fireEvent.change(screen.getByPlaceholderText("ex) 부산"), {
      target: { value: "부산" },
    });
    fireEvent.change(screen.getByPlaceholderText("ex) 3"), {
      target: { value: "5" },
    });

    const today = new Date("2025-05-15");
    const end = new Date("2025-05-18");

    fireEvent.change(screen.getByPlaceholderText("시작일 선택"), {
      target: { value: today },
    });
    fireEvent.change(screen.getByPlaceholderText("종료일 선택"), {
      target: { value: end },
    });

    fireEvent.click(screen.getByText("예상 예산 출력하기"));

    expect(await screen.findByText(/코멘트/)).toBeInTheDocument();
    expect(document.querySelector("canvas")).toBeInTheDocument();
  });
});