#!/bin/bash
mkdir -p ~/backups
cp ~/ia_shared/db/nexus.db ~/backups/nexus_$(date +%Y%m%d_%H%M%S).db
find ~/backups -name "nexus_*.db" -mtime +7 -delete
