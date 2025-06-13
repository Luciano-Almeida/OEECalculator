import { useAuth } from "../context/AuthContext";
import { auditService } from "../services/auditService";

export const useAuditoria = () => {
    const {usuario} = useAuth();

    const registrarAuditoria = async (tela, acao, detalhe) => {
        if (!usuario) return;

        await auditService.log({
            usuario: usuario.nome,
            tela,
            acao,
            detalhe
        });
    };

    return { registrarAuditoria };
};