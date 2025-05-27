import React, { useState, useEffect } from "react";
import { Doughnut } from "react-chartjs-2";
import axios from "axios";
import { render, screen } from "@testing-library/react";
import Budget from "../pages/Budget.jsx";
import { MemoryRouter } from "react-router-dom";

global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
}

describe("예산 계산 페이지 테스트", () => {
  test("예산 정보가 올바르게 렌더링됨", async () => {
    render(
      <MemoryRouter>
        <Budget />
      </MemoryRouter>
    );

    expect(await screen.findByText(/₩\s*720,000/)).toBeInTheDocument();
  });
});