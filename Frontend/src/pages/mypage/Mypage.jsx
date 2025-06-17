import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";
import Header from "../../components/Header";

export default function Mypage() {
  const [schedules, setSchedules] = useState([]);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {

      try {
        const token = localStorage.getItem("accessToken");
        const res = await axios.get(
          `${import.meta.env.VITE_API_BASE_URL}/mypage`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        setUser(res.data);
      } catch (err) {
        console.error("사용자 정보 조회 실패:", err);
      }
    };

    const fetchSchedules = async () => {
      try {
        const token = localStorage.getItem("accessToken");
        const res = await axios.get(
          `${import.meta.env.VITE_API_BASE_URL}/mypage/schedules
`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        setSchedules(res.data);
      } catch (err) {
        console.error("스케줄 조회 실패:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
    fetchSchedules();
  }, []);

  if (isLoading) return <div className="text-center mt-10">불러오는 중...</div>;

  return (
    <>
      <Header />
      <div className="max-w-3xl mx-auto mt-10 px-4 py-8 bg-white rounded-lg shadow-md">
        {user && (
          <div className="mb-6 text-center">
            <p className="text-xl font-semibold">
              {user.username}님의 마이페이지
            </p>
            <p className="text-gray-600 text-sm">{user.email}</p>
          </div>
        )}
        <h1 className="text-2xl font-bold mb-6">내 일정 목록</h1>
        {schedules.length === 0 ? (
          <p>저장된 일정이 없습니다.</p>
        ) : (
          <ul className="space-y-4">
            {schedules.map((item) => (
              <li
                key={item.id}
                className="p-6 border rounded-lg shadow hover:shadow-lg transition-shadow"
              >
                <div className="font-bold text-lg text-blue-600">
                  {item.end_city} 여행
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {item.start_date} ~ {item.end_date}
                </div>
                <div className="mt-4 text-right">
                  <button
                    onClick={() => navigate(`/TravelPlan/${item.id}`)}
                    className="bg-blue-600 text-white text-sm px-4 py-2 rounded hover:bg-blue-700"
                  >
                    상세 보기
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}