rem -P asks for the password of the new django user; put it in DATABASE_URL in hidos\.env
createuser -s -P -U postgres django
createdb -U postgres --owner django django hidos-django