import { Link } from "react-router-dom";
const Header = () => {
  return (
    <header className="px-8 py-4 shadow bg-white border-b">
      <div className="relative flex justify-between items-center w-full max-w-7xl mx-auto mt-3 mb-3">
        <div className="absolute left-0">
          <Link to="/" className="flex items-center text-xl md:text-2xl font-bold text-blue-600 tracking-tight">
            <img src="/logo.png" alt="로고" className="w-8 mr-2 h-auto"/>
            거기 어때
          </Link>
        </div>
        <nav className="absolute left-1/2 transform -translate-x-1/2 flex gap-8 text-base md:text-lg font-medium">
          <Link to="/" className="hover:text-blue-600 hover:underline">
            홈
          </Link>
          <Link to="/TravelStyleForm" className="hover:text-blue-600 hover:underline">
            여행 플래너
          </Link>
          <Link to="/RestaurantInput" className="hover:text-blue-600 hover:underline">
            맛집 추천
          </Link>
          <Link to="/BudgetInput" className="hover:text-blue-600 hover:underline">
            예산 계산
          </Link>
        </nav>
        <div className="flex gap-2">
          {/* <button className="text-sm text-blue-600">
            <Link to="/Login">로그인</Link>
          </button>
          <button className="text-sm bg-blue-600 text-white px-4 py-1 rounded">
            <Link to="/Signup">회원가입</Link>
          </button> */}
        </div>
      </div>
    </header>
  );
};

export default Header;