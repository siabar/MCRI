#create network in docker for communication between readbiomed/mcri_rfv and ontoserver
docker network create  --driver=bridge   --subnet=100.100.0.0/16   --gateway=100.100.0.1  rfv_ontoserver

# Start the compose ontoserver
cd docker_ontoserver
docker-compose up -d
# Get the latest version of SNOMED CT-AU into the Ontoserver index
docker exec ontoserver /index.sh -s sctau

# Download the version (2020) of MetaMap (Full download) and copy in ocker_rfv directory
cd ../docker_rfv
