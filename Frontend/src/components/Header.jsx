import { Link } from "react-router-dom";
const Header = () => {
  return (
    <header className="flex justify-between items-center px-8 py-4 shadow">
      <Link to="/" className="flex items-center text-xl font-bold text-blue-600">
        <img src="/logo.png" alt="로고" className="w-8 mr-2 h-auto"/>
        거기 어때
      </Link>
      <nav className="flex gap-6 text-sm">
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
      </nav>
      <div className="flex gap-2">
        {/* <button className="text-sm text-blue-600">
          <Link to="/Login">로그인</Link>
        </button>
        <button className="text-sm bg-blue-600 text-white px-4 py-1 rounded">
          <Link to="/Signup">회원가입</Link>
        </button> */}
      </div>
    </header>
  );
};

export default Header;