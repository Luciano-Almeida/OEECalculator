/* EXEMPLOS DE USO
Log único:
await auditService.log({
      usuario: 'joao',
      tela: 'CadastroCliente',
      acao: 'Criar',
      detalhe: 'Cliente cadastrado com sucesso'
    });
  };
*/


/*
Logs Múltiplos
await auditService.logMultiple([
  {
    usuario: 'joao',
    tela: 'Login',
    acao: 'Autenticação',
    detalhe: 'Login bem-sucedido'
  },
  {
    usuario: 'joao',
    tela: 'Painel',
    acao: 'Acesso',
    detalhe: 'Entrou no painel'
  }
]);
*/





import axios from "axios";

const API_URL = 'http://localhost:8000/criar_auditoria';

export const auditService = {
    log: async ({ usuario, tela, acao, detalhe }) => {
        try {
            await axios.post(API_URL, {
                usuario,
                tela,
                acao,
                detalhe
            });
        } catch (error) {
            console.error("Erro ao enviar auditoria:", error);
        }
    },

    logMultiple: async (registros = []) => {
        const promises = registros.map(reg => auditService.log(reg));
        await Promise.all(promises);
    }

};