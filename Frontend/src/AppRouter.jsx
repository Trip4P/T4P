import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Main from './pages/Main.jsx';
import TravelStyleForm from './pages/TravelStyleForm.jsx';
import TravelPlan from './pages/TravelPlan.jsx';
import PlaceDetailPage from './pages/PlaceDetail.jsx';
import Budget from './pages/Budget.jsx';
import BudgetInput from './pages/BudgetInput.jsx';
import RestaurantInput from './pages/RestaurantInput.jsx'
import RestaurantRecommend from './pages/RestaurantRecommend.jsx'
import RestaurantDetail from './pages/RestaurantDetail.jsx'
import Signup from './pages/Signup.jsx';
import Login from './pages/Login.jsx';
import MyPlan from './pages/MyPlan.jsx';

export default function AppRouter() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Main />} />
        <Route path="/TravelStyleForm" element={<TravelStyleForm />} />
        <Route path="/TravelPlan" element={<TravelPlan />} />
        <Route path="/PlaceDetailPage" element={<PlaceDetailPage />} />
        <Route path="/Budget" element={<Budget />} />
        <Route path="/BudgetInput" element={<BudgetInput />} />
        <Route path="/RestaurantInput" element={<RestaurantInput />} />
        <Route path="/RestaurantRecommend" element={<RestaurantRecommend />} />
        <Route path="/RestaurantDetail" element={<RestaurantDetail />} />
        <Route path="/Signup" element={<Signup />} />
        <Route path="/Login" element={<Login />} />
        <Route path="/MyPlan" element={<MyPlan />} />
      </Routes>
    </Router>
  )
}