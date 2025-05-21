import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Main from './pages/Main.jsx';
import TravelStyleForm from './pages/TravelStyleForm.jsx';
import TravelPlan from './pages/TravelPlan.jsx';
import Budget from './pages/Budget.jsx';
import BudgetInput from './pages/BudgetInput.jsx';
import HotPlaceInput from './pages/HotPlaceInput.jsx'
import HotPlaceRecommend from './pages/HotPlaceRecommend.jsx'
import HotPlaceDetail from './pages/HotPlaceDetail.jsx'

export default function AppRouter() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Main />} />
        <Route path="/TravelStyleForm" element={<TravelStyleForm />} />
        <Route path="/TravelPlan" element={<TravelPlan />} />
        <Route path="/Budget" element={<Budget />} />
        <Route path="/BudgetInput" element={<BudgetInput />} />
        <Route path="/HotPlaceInput" element={<HotPlaceInput />} />
        <Route path="/HotPlaceRecommend" element={<HotPlaceRecommend />} />
        <Route path="/HotPlaceDetail" element={<HotPlaceDetail />} />
      </Routes>
    </Router>
  )
}