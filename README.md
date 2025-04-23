docker-compose down -v  # Remove volumes para garantir limpeza total




# descobrir IP para PGAdmin4
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres-db-backend


# rodar banco de dados direto do powerShell
docker exec -it postgres-db-backend psql -U backend_user -d backend_database
### select * from camera_name;





para criar a nova célula sem precisar apagar tudo
ALTER TABLE oee_setup
ADD COLUMN shifts JSONB;

