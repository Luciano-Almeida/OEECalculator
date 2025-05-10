docker-compose down -v  # Remove volumes para garantir limpeza total




# descobrir IP para PGAdmin4
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres-db-backend


# rodar banco de dados direto do powerShell
docker exec -it postgres-db-backend psql -U backend_user -d backend_database
### select * from camera_name;





para criar a nova célula sem precisar apagar tudo
ALTER TABLE oee_setup
ADD COLUMN shifts JSONB;














GIT Tipos de Commit
Exemplo "feat(auth): adiciona JWT ao login"
feat	    Adição de nova funcionalidade
fix	        Correção de bug
chore	    Tarefas menores ou de manutenção (ex: ajustes de build, configs, dependências)
docs	    Alterações na documentação
style	    Mudanças de formatação, indentação, espaços, sem afetar código
refactor	Refatorações de código (sem alterar comportamento nem corrigir bugs)
test	    Adição ou modificação de testes
perf	    Melhorias de performance
build	    Mudanças em arquivos de build ou dependências externas (ex: webpack, npm)
ci	        Mudanças em arquivos de integração contínua (ex: GitHub Actions, Travis)
revert	    Reversão de um commit anterior
