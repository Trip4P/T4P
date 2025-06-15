import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

export default function Header () {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    setIsLoggedIn(false);
    navigate("/Login");
  };

  return (
    <header className="px-8 py-4 shadow bg-white">
      <div className="flex justify-between items-center w-full max-w-7xl mx-auto">
        <div className="flex-shrink-0">
          <Link to="/" className="flex items-center text-xl md:text-2xl font-bold text-blue-600 tracking-tight">
            <img src="/logo.png" alt="로고" className="w-8 mr-2 h-auto"/>
            거기 어때
          </Link>
        </div>
        <nav className="flex gap-8 text-base md:text-lg font-medium">
          <Link to="/" className="hover:text-blue-600">
            홈
          </Link>
          <Link to="/TravelStyleForm" className="hover:text-blue-600">
            여행 플래너
          </Link>
          <Link to="/RestaurantInput" className="hover:text-blue-600">
            맛집 추천
          </Link>
          <Link to="/BudgetInput" className="hover:text-blue-600">
            예산 계산
          </Link>
          <Link to="/Mypage" className="hover:text-blue-600">
            마이 페이지
          </Link>
        </nav>
        <div className="flex gap-2">
          {isLoggedIn ? (
            <button onClick={handleLogout} className="text-sm text-blue-500 self-center">
              로그아웃
            </button>
          ) : (
            <>
              <Link to="/Login" className="text-sm text-blue-600 self-center">
                로그인
              </Link>
              <Link to="/Signup" className="text-sm bg-blue-600 text-white px-4 py-1 rounded">
                회원가입
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
};