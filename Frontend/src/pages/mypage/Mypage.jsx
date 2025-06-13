import { useEffect, useState } from "react";
import axios from "axios";

export default function Mypage() {
  const [schedules, setSchedules] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSchedules = async () => {
      try {
        const token = localStorage.getItem("accessToken");
        const res = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/mypage/schedules
`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setSchedules(res.data);
      } catch (err) {
        console.error("스케줄 조회 실패:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSchedules();
  }, []);

  if (isLoading) return <div className="text-center mt-10">불러오는 중...</div>;

  return (
    <div className="max-w-3xl mx-auto mt-10 px-4">
      <h1 className="text-2xl font-bold mb-6">내 일정 목록</h1>
      {schedules.length === 0 ? (
        <p>저장된 일정이 없습니다.</p>
      ) : (
        <ul className="space-y-4">
          {schedules.map((item) => (
            <li key={item.id} className="p-4 border rounded shadow">
              <div className="font-semibold text-lg">{item.end_city} 여행</div>
              <div className="text-sm text-gray-600">
                {item.start_date} ~ {item.end_date}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}