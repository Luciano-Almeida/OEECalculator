import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TrilhaDeAuditoria = () => {
  const [searchParams, setSearchParams] = useState({
    user: '',
    startDate: '',
    endDate: '',
  });

  const [users, setUsers] = useState([]);  // Lista de usuários (para o dropdown)
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // Carregar a lista de usuários quando o componente é montado
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        // Exemplo de chamada de API com Axios para buscar os usuários
        console.log("Carregando usuários.")
        const response = await axios.get('http://localhost:8000/users');
        setUsers(response.data);  // Atualiza a lista de usuários com a resposta
        console.log("usuários:", response.data);
      } catch (error) {
        console.error('Erro ao carregar a lista de usuários:', error);
      }
    };

    fetchUsers();
  }, []);

  const handleChange = (e) => {
    setSearchParams({
      ...searchParams,
      [e.target.name]: e.target.value,
    });
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Verifica se a data final é maior que a inicial
    if (new Date(searchParams.endDate) < new Date(searchParams.startDate)) {
      alert('A data final não pode ser anterior à data inicial.');
      setLoading(false);
      return;
    }

    try {
      // Chamada à API para buscar os registros da trilha de auditoria com Axios
      const response = await axios.get('http://localhost:8000/audit-trail', {
        params: {
          userID: searchParams.user,
          startDate: searchParams.startDate,
          endDate: searchParams.endDate,
        },
      });
      setResults(response.data);  // Atualiza os resultados com a resposta da API
    } catch (error) {
      console.error('Erro ao buscar trilha de auditoria:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Pesquisar Trilha de Auditoria</h2>
      <form onSubmit={handleSearch}>
        <div>
          <label htmlFor="user">Usuário</label>
          <select
            name="user"
            id="user"
            value={searchParams.user}
            onChange={handleChange}
            required
          >
            <option value="">Selecione um usuário</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="startDate">Período Inicial</label>
          <input
            type="date"
            name="startDate"
            value={searchParams.startDate}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label htmlFor="endDate">Período Final</label>
          <input
            type="date"
            name="endDate"
            value={searchParams.endDate}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <button type="submit" disabled={loading}>
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>
      </form>

      <hr />

      <h3>Resultados</h3>
      {results.length === 0 ? (
        <p>Nenhum resultado encontrado.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Usuário</th>
              <th>Ação</th>
              <th>Data</th>
              <th>Detalhes</th>
            </tr>
          </thead>
          <tbody>
            {results.map((entry, index) => (
              <tr key={index}>
                <td>{entry.user}</td>
                <td>{entry.action}</td>
                <td>{entry.date}</td>
                <td>{entry.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default TrilhaDeAuditoria;
