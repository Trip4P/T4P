import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Main from './pages/Main.jsx';
import TravelStyleForm from './pages/travel/TravelStyleForm.jsx';
import TravelPlan from './pages/travel/TravelPlan.jsx';
import PlaceDetail from './pages/travel/PlaceDetail.jsx';
import Budget from './pages/travel/Budget.jsx';
import BudgetInput from './pages/BudgetInput.jsx';
import RestaurantInput from './pages/restaurant/RestaurantInput.jsx'
import RestaurantRecommend from './pages/restaurant/RestaurantRecommend.jsx'
import RestaurantDetail from './pages/restaurant/RestaurantDetail.jsx'
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
        <Route path="/PlaceDetail" element={<PlaceDetail />} />
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