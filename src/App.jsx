import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';
import PotentialCustomers from './pages/PotentialCustomers';
import ServiceMix from './pages/ServiceMix';
import ActionCenter from './pages/ActionCenter';
import CustomerMovement from './pages/CustomerMovement';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  return (
    <Router>
      <div className="flex h-screen overflow-hidden bg-vnpost-bg">
        <Sidebar />
        <div className="flex flex-col flex-1 overflow-hidden">
          <Topbar />
          <main className="flex-1 overflow-y-auto p-6 md:p-8">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/customers" element={<Customers />} />
              <Route path="/potential" element={<PotentialCustomers />} />
              <Route path="/service-mix" element={<ServiceMix />} />
              <Route path="/action-center" element={<ActionCenter />} />
              <Route path="/customer-movement" element={<CustomerMovement />} />
            </Routes>
          </main>
        </div>
      </div>
      <ToastContainer position="bottom-right" autoClose={3000} />
    </Router>
  );
}

export default App;
