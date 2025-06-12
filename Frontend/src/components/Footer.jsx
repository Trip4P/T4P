import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="bg-white text-sm text-gray-600 px-6 py-8">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center space-y-6 md:space-y-0">
        <div>
          <div className="text-lg font-bold text-blue-600 mb-2">거기 어때 AI</div>
          <p className="text-gray-600">AI 기술로 당신의 완벽한 여행을 설계해드립니다.</p>
        </div>
        <div>
          <h4 className="text-base font-semibold mb-2 text-gray-800">서비스</h4>
          <ul className="flex flex-row space-x-4">
            <li>
              <Link to="/TravelStyleForm" className="hover:text-blue-600 transition-colors">
                여행 플래너
              </Link>
            </li>
            <li>
              <Link to="/RestaurantInput" className="hover:text-blue-600 transition-colors">
                맛집 추천
              </Link>
            </li>
            <li>
              <Link to="/BudgetInput" className="hover:text-blue-600 transition-colors">
                예산 계산
              </Link>
            </li>
          </ul>
        </div>
      </div>
      <div className="mt-8 text-center text-xs text-gray-500">
        © 2025 T4P. All rights reserved.
      </div>
    </footer>
  );
}
