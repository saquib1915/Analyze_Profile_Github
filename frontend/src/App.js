import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "@/pages/Dashboard";
import { Toaster } from "sonner";

function App() {
  return (
    <div className="App min-h-screen bg-white text-zinc-950">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="bottom-right" theme="light" />
    </div>
  );
}

export default App;
