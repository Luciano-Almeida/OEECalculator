import { useState } from 'react';

import './App.css';
import { AuthProvider, useAuth} from './context/AuthContext'
import MainContent from './Components/MainContent';

function App() {
  const [currentPage, setCurrentPage] = useState('OEEDinamico');
  const [open, setOpen] = useState(false);

  return (
    <AuthProvider>
      <MainContent
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        open={open}
        setOpen={setOpen}
      />
    </AuthProvider>
  );
}

export default App;








