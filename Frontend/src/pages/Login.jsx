import axios from "axios";
import { useState } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Login() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!form.username || !form.email || !form.password) {
      setError("닉네임과 이메일과 비밀번호를 입력해주세요.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/auth/login", form);

      console.log("로그인 성공:", response.data);
      alert("로그인 성공!");
      setForm({ username: "", email: "", password: "" });
    } catch (err) {
      if (err.response) {
        if (err.response.status === 401) {
          setError("이메일 또는 비밀번호가 올바르지 않습니다.");
        } else {
          setError("로그인에 실패했습니다. 다시 시도해주세요.");
        }
      } else {
        console.error("에러 발생:", err);
        setError("네트워크 오류가 발생했습니다.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Header />
      <div className="max-w-md mx-auto mt-10 p-6 border rounded shadow">
        <h2 className="text-2xl font-semibold mb-4">로그인</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-1">닉네임</label>
            <input
              type="text"
              name="username"
              value={form.username}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded"
              required
            />
          </div>
          <div>
            <label className="block mb-1">이메일</label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded"
              required
            />
          </div>
          <div>
            <label className="block mb-1">비밀번호</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded"
              required
            />
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
            disabled={isLoading}
          >
            {isLoading ? <LoadingSpinner /> : "로그인"}
          </button>
        </form>
      </div>
      <Footer />
    </>
  );
}