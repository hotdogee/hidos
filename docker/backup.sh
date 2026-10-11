#!/bin/sh
# Back up the docker compose stack (#25): a PostgreSQL dump and a tarball of
# the uploaded images / analysis results (the "media" volume).
#
#   docker/backup.sh [backup-dir]        (default: ./backups)
#
# Restore:
#   docker compose exec -T db pg_restore -U django -d django --clean --if-exists < BACKUP/django.dump
#   docker run --rm -v hidos_media:/data/media -v "$PWD/BACKUP:/backup" alpine \
#       sh -c 'cd /data && tar xzf /backup/media.tar.gz'
#
# Run it from cron, then copy the backup directory off the machine.
set -eu
cd "$(dirname "$0")/.."
dest="${1:-backups}/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$dest"
docker compose exec -T db pg_dump -U django -Fc django > "$dest/django.dump"
docker run --rm -v hidos_media:/data/media:ro -v "$(cd "$dest" && pwd):/backup" alpine \
    tar czf /backup/media.tar.gz -C /data media
echo "Backup written to $dest"
