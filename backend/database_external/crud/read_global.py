import logging
from sqlalchemy import text
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

# Logger específico
logger = logging.getLogger(__name__)

# 📌 Função genérica para executar consultas (assíncrona)
async def fetch_all(db: AsyncSession, stmt):
    try:
        result = await db.execute(stmt)  # Execução assíncrona
        return result.scalars().all()  # Obtém todos os resultados
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao buscar registros: {e}")
        raise

async def fetch_one(db: AsyncSession, stmt):
    try:
        result = await db.execute(stmt)  # Execução assíncrona
        return result.scalar_one_or_none()  # Obtém um único registro ou None
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao buscar registro: {e}")
        raise

async def fetch_all_rows(db: AsyncSession, stmt):
    """ Para selects com múltiplas colunas (e.g., JOIN, funções agregadas), 
        use .all() ao invés de .scalars().all().
    """
    try:
        result = await db.execute(stmt)
        return result.all()  # Retorna todas as linhas como tuplas
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao buscar registros: {e}")
        raise


# 📌 Funções de leitura para cada tabela
# 🔍 Busca o último ID ativo da tabela Global
async def get_last_active_user_id(db: AsyncSession):
    query = text("""SELECT "usuarioAtivo_ID" FROM "Global";""")
    result = await fetch_all_rows(db, query)

    if not result or result[0][0] is None:
        #raise HTTPException(status_code=404, detail="Nenhum usuário ativo encontrado")
        return None
    
    # Extrai apenas os IDs de cada tupla e cria uma lista
    usuario_ativo_ids = [row[0] for row in result]

    if not usuario_ativo_ids:
        #raise HTTPException(status_code=404, detail="Lista de IDs de usuários vazia")
        return None

    return usuario_ativo_ids[0]  # Retorna o último ID da lista

# 🔍 Busca nome e nível de acesso de um usuário pelo ID
async def get_user_info_by_id(db: AsyncSession, user_id: int):
    query = text("""
        SELECT "Nome", "NivelAcesso_ID"
        FROM "Usuarios"
        WHERE "ID" = :user_id;
    """).bindparams(user_id=user_id)

    result = await fetch_all_rows(db, query)

    if not result:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    nome, nivel_acesso = result[0]
    return {"id": user_id, "nome": nome, "nivel_acesso": nivel_acesso}

# 🔍 Busca permissões para um nível de acesso
async def get_permissoes_ativas_por_nivel_acesso(db: AsyncSession, nivel_acesso_id: int):
    """
    Retorna todas as permissões ativas (valor = true) associadas a um determinado nível de acesso.

    Executa uma consulta SQL direta na tabela "PermissoesOEE" para buscar os nomes das permissões
    vinculadas ao nível de acesso informado, cujo valor seja verdadeiro.

    Args:
        db (AsyncSession): Sessão de banco de dados assíncrona.
        nivel_acesso_id (int): ID do nível de acesso desejado.

    Returns:
        dict: Um dicionário contendo o ID do nível de acesso e uma lista com os nomes das permissões ativas.
              Exemplo:
              {
                  "nivel_acesso_id": 2,
                  "permissoes": ["VisualizarRelatorio", "EditarParametros"]
              }

    Raises:
        HTTPException: Se nenhuma permissão ativa for encontrada para o nível de acesso informado.
    """
    query = text("""
        SELECT "permissao"
        FROM "PermissoesOEE"
        WHERE "NivelAcesso_ID" = :nivel_acesso_id
        AND "valor" = true;
    """).bindparams(nivel_acesso_id=nivel_acesso_id)

    result = await fetch_all_rows(db, query)

    if not result:
        raise HTTPException(status_code=404, detail="Nenhuma permissão encontrada para esse nível de acesso")

    permissoes = [row[0] for row in result]

    return {"nivel_acesso_id": nivel_acesso_id, "permissoes": permissoes}





